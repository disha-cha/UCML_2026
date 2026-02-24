#!/usr/bin/env python
"""
uc_features.py

Extract UC-specific EXOGENOUS INSTANCE METADATA for L2Sep from .minud.json sidecars.

This version is aligned with a **copper-plate stochastic UC** generator:
- NO enforceable transmission (no PTDF/angles/line flows)
- First-stage binaries shared across scenarios: u, v, w
- Second-stage continuous per scenario: p, r
- Slack variables per (s,t): load_shed, spill, res_short

Therefore, "network structure" features like n_lines/density are removed.
We keep only n_buses as a dimension proxy (optional), since it may correlate with size
in your dataset but does not affect feasibility/optimality directly in copper-plate UC.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division avoiding div-by-zero."""
    return a / b if abs(b) > 1e-12 else default


def _as_float_dict(d: Dict[str, Any]) -> Dict[str, float]:
    return {str(k): float(v) for k, v in (d or {}).items()}


def _as_int_dict(d: Dict[str, Any]) -> Dict[str, int]:
    return {str(k): int(v) for k, v in (d or {}).items()}


# -----------------------------------------------------------------------------
# Feature container
# -----------------------------------------------------------------------------

@dataclass
class UCFeatures:
    """
    Container for UC-specific exogenous instance metadata.

    All features are computable directly from the .minud.json sidecar,
    without requiring SCIP or any solver-dependent quantities.
    """

    # -------------------------
    # Generator / capacity stats
    # -------------------------
    n_generators: int
    total_capacity: float
    capacity_cv: float                   # std(Pmax)/mean(Pmax)
    min_max_capacity_ratio: float         # min(Pmax)/max(Pmax)

    avg_pmin_frac: float                 # mean(Pmin/Pmax)  (lower = more flexible)
    avg_headroom_frac: float             # mean((Pmax-Pmin)/Pmax) (higher = more headroom)

    # -------------------------
    # Min up/down coupling
    # -------------------------
    avg_min_uptime: float
    avg_min_downtime: float
    max_min_uptime: int
    updown_asymmetry: float              # mean(Ton-Toff)

    # -------------------------
    # Temporal / scenario structure
    # -------------------------
    n_time_periods: int
    n_scenarios: int
    demand_cv: float
    peak_to_avg_demand: float
    demand_range_normalized: float       # (max-min)/mean

    # -------------------------
    # Reserve structure
    # -------------------------
    avg_reserve_ratio: float             # mean(Reserve/Demand)

    # -------------------------
    # Dimension proxies (copper-plate: not structural)
    # -------------------------
    n_buses: int
    generator_to_bus_ratio: float

    # -------------------------
    # Coupling / hardness proxies from dimensions
    # -------------------------
    binary_var_fraction: float
    first_stage_fraction: float
    temporal_coupling_ratio: float       # max(minup, mindown) / T

    def to_array(self) -> np.ndarray:
        return np.array(
            [
                self.n_generators,
                self.total_capacity,
                self.capacity_cv,
                self.min_max_capacity_ratio,
                self.avg_pmin_frac,
                self.avg_headroom_frac,
                self.avg_min_uptime,
                self.avg_min_downtime,
                self.max_min_uptime,
                self.updown_asymmetry,
                self.n_time_periods,
                self.n_scenarios,
                self.demand_cv,
                self.peak_to_avg_demand,
                self.demand_range_normalized,
                self.avg_reserve_ratio,
                self.n_buses,
                self.generator_to_bus_ratio,
                self.binary_var_fraction,
                self.first_stage_fraction,
                self.temporal_coupling_ratio,
            ],
            dtype=np.float32,
        )

    @staticmethod
    def feature_names() -> List[str]:
        return [
            "n_generators",
            "total_capacity",
            "capacity_cv",
            "min_max_capacity_ratio",
            "avg_pmin_frac",
            "avg_headroom_frac",
            "avg_min_uptime",
            "avg_min_downtime",
            "max_min_uptime",
            "updown_asymmetry",
            "n_time_periods",
            "n_scenarios",
            "demand_cv",
            "peak_to_avg_demand",
            "demand_range_normalized",
            "avg_reserve_ratio",
            "n_buses",
            "generator_to_bus_ratio",
            "binary_var_fraction",
            "first_stage_fraction",
            "temporal_coupling_ratio",
        ]

    @staticmethod
    def n_features() -> int:
        return 21


# -----------------------------------------------------------------------------
# Core extraction
# -----------------------------------------------------------------------------

def extract_uc_features(metadata: Dict[str, Any], n_scenarios: int = 1) -> UCFeatures:
    """
    Extract UC-specific exogenous metadata from the .minud.json sidecar.

    Expected keys (from your generator):
      - Pmax, Pmin (dicts keyed by generator id as strings)
      - Lup, Ldown (dicts keyed by generator id as strings)
      - Demand (list length T)
      - Reserve (list length T)
      - times (list length T)
      - buses (list) or n_buses
      - n_scenarios
    """
    n_scenarios = int(metadata.get("n_scenarios", n_scenarios))

    Pmax = _as_float_dict(metadata.get("Pmax", {}))
    Pmin = _as_float_dict(metadata.get("Pmin", {}))
    Lup = _as_int_dict(metadata.get("Lup", {}))
    Ldown = _as_int_dict(metadata.get("Ldown", {}))

    n_gen = max(len(Pmax), 1)

    # --- capacities
    pmax_vals = np.array(list(Pmax.values()), dtype=float) if Pmax else np.array([100.0], dtype=float)

    # align pmin with pmax keys when possible
    if Pmax:
        pmin_vals = np.array([float(Pmin.get(g, 0.2 * Pmax[g])) for g in Pmax.keys()], dtype=float)
    else:
        pmin_vals = np.array([20.0], dtype=float)

    total_capacity = float(np.sum(pmax_vals))
    pmax_mean = float(np.mean(pmax_vals))
    capacity_cv = float(safe_divide(float(np.std(pmax_vals)), pmax_mean))
    min_max_capacity_ratio = float(safe_divide(float(np.min(pmax_vals)), float(np.max(pmax_vals))))

    # flexibility proxies
    pmin_frac = np.array([safe_divide(pmin_vals[i], pmax_vals[i], default=0.2) for i in range(len(pmax_vals))], dtype=float)
    avg_pmin_frac = float(np.mean(pmin_frac))
    avg_headroom_frac = float(np.mean(1.0 - pmin_frac))

    # --- up/down times (if missing, default mild coupling)
    if Lup:
        lup_vals = np.array(list(Lup.values()), dtype=int)
        # use matching keys where possible
        ldown_vals = np.array([int(Ldown.get(g, np.median(list(Ldown.values())) if Ldown else 2)) for g in Lup.keys()], dtype=int) if Lup else np.array([2], dtype=int)
    else:
        lup_vals = np.array([2], dtype=int)
        ldown_vals = np.array([2], dtype=int)

    avg_min_uptime = float(np.mean(lup_vals))
    avg_min_downtime = float(np.mean(ldown_vals))
    max_min_uptime = int(np.max(lup_vals))
    updown_asymmetry = float(np.mean(lup_vals - ldown_vals))

    # --- time/scenarios
    times = metadata.get("times", list(range(1, 25)))
    n_time_periods = int(len(times)) if times else 24

    demand = metadata.get("Demand", [])
    reserve = metadata.get("Reserve", [])

    if demand and len(demand) > 0:
        demand_arr = np.array(demand, dtype=float)
        dmean = float(np.mean(demand_arr))
        demand_cv = float(safe_divide(float(np.std(demand_arr)), dmean))
        peak_to_avg_demand = float(safe_divide(float(np.max(demand_arr)), dmean))
        demand_range_normalized = float(safe_divide(float(np.max(demand_arr) - np.min(demand_arr)), dmean))
    else:
        # fallback if missing
        dmean = 0.6 * total_capacity
        demand_cv = 0.15
        peak_to_avg_demand = 1.3
        demand_range_normalized = 0.4

    if reserve and demand and len(reserve) == len(demand):
        reserve_ratios = [safe_divide(float(r), float(d), default=0.0) for r, d in zip(reserve, demand)]
        avg_reserve_ratio = float(np.mean(reserve_ratios))
    elif reserve and len(reserve) > 0:
        avg_reserve_ratio = float(safe_divide(float(np.mean(np.array(reserve, dtype=float))), dmean))
    else:
        avg_reserve_ratio = 0.10

    # --- buses (dimension proxy)
    buses = metadata.get("buses", [])
    n_buses = int(len(buses)) if buses else int(metadata.get("n_buses", n_gen))
    generator_to_bus_ratio = float(safe_divide(n_gen, n_buses))

    # --- coupling / hardness proxies from dimensions
    # Copper-plate stochastic UC (as implemented):
    # First-stage binaries: u,v,w  -> 3*G*T
    # Second-stage continuous: p,r -> 2*G*T*S
    # Slack vars per (s,t): load_shed, spill, res_short -> 3*T*S
    n_binary = 3 * n_gen * n_time_periods
    n_continuous = (2 * n_gen * n_time_periods * n_scenarios) + (3 * n_time_periods * n_scenarios)
    total_vars = n_binary + n_continuous

    binary_var_fraction = float(safe_divide(n_binary, total_vars))
    first_stage_fraction = float(safe_divide(n_binary, total_vars))  # first-stage == binaries in this model

    temporal_coupling_ratio = float(
        safe_divide(
            float(max(int(np.max(lup_vals)), int(np.max(ldown_vals)))),
            float(n_time_periods),
        )
    )

    return UCFeatures(
        n_generators=n_gen,
        total_capacity=float(total_capacity),
        capacity_cv=float(capacity_cv),
        min_max_capacity_ratio=float(min_max_capacity_ratio),
        avg_pmin_frac=float(avg_pmin_frac),
        avg_headroom_frac=float(avg_headroom_frac),
        avg_min_uptime=float(avg_min_uptime),
        avg_min_downtime=float(avg_min_downtime),
        max_min_uptime=int(max_min_uptime),
        updown_asymmetry=float(updown_asymmetry),
        n_time_periods=int(n_time_periods),
        n_scenarios=int(n_scenarios),
        demand_cv=float(demand_cv),
        peak_to_avg_demand=float(peak_to_avg_demand),
        demand_range_normalized=float(demand_range_normalized),
        avg_reserve_ratio=float(avg_reserve_ratio),
        n_buses=int(n_buses),
        generator_to_bus_ratio=float(generator_to_bus_ratio),
        binary_var_fraction=float(binary_var_fraction),
        first_stage_fraction=float(first_stage_fraction),
        temporal_coupling_ratio=float(temporal_coupling_ratio),
    )


def extract_features_from_sidecar(sidecar_path: str, n_scenarios: int = 1) -> UCFeatures:
    with open(sidecar_path, "r") as f:
        metadata = json.load(f)
    return extract_uc_features(metadata, n_scenarios=n_scenarios)


def normalize_features(features: np.ndarray, stats: Optional[Dict[str, np.ndarray]] = None) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Normalize features to zero mean, unit variance.
    """
    if features.ndim == 1:
        features = features.reshape(1, -1)

    if stats is None:
        stats = {"mean": np.mean(features, axis=0), "std": np.std(features, axis=0) + 1e-8}

    normalized = (features - stats["mean"]) / stats["std"]
    return normalized.squeeze(), stats


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import glob

    parser = argparse.ArgumentParser(description="Extract UC features from .minud.json sidecars (copper-plate)")
    parser.add_argument("--input-dir", required=True, help="Directory containing .minud.json files")
    parser.add_argument("--output", required=True, help="Output .npz file path")
    args = parser.parse_args()

    sidecar_files = sorted(glob.glob(str(Path(args.input_dir) / "*.minud.json")))
    print(f"Found {len(sidecar_files)} sidecar files")

    all_features = []
    instance_names = []

    for sf in sidecar_files:
        try:
            feats = extract_features_from_sidecar(sf)
            all_features.append(feats.to_array())
            instance_names.append(Path(sf).name.replace(".minud.json", ""))
            print(f"  Extracted: {Path(sf).name}")
        except Exception as e:
            print(f"  FAILED: {Path(sf).name} - {e}")

    if not all_features:
        raise SystemExit("No features extracted (all failed).")

    X = np.stack(all_features, axis=0)
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"n_features: {X.shape[1]}")
    print(f"Feature names: {UCFeatures.feature_names()}")

    np.savez(
        args.output,
        features=X,
        feature_names=np.array(UCFeatures.feature_names(), dtype=object),
        instance_names=np.array(instance_names, dtype=object),
    )
    print(f"Saved to {args.output}")
