#!/usr/bin/env python3
"""
collect_uc_times.py

Run SCIP on UC instances under a small, fixed configuration set A (size = 10),
and record reward = solve_time_sec.

Writes:
  outputs_step3_collect_time/
    configs.json
    results.csv
    results.jsonl

Usage (WSL):
  source /mnt/c/Users/disha/OneDrive/Documents/l2sep_scip/PySCIPOpt-siruil/.venv/bin/activate
  export SCIP_PREFIX=$HOME/scipopt
  export LD_LIBRARY_PATH="$SCIP_PREFIX/lib:$LD_LIBRARY_PATH"

  python collect_uc_times.py \
    --manifest "/mnt/c/Users/disha/OneDrive/Documents/instances/manifest.json" \
    --outdir "outputs_step3_collect_time" \
    --time-limit 300 \
    --seed 0
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

from pyscipopt import Model


# -----------------------------
# Config definitions
# -----------------------------

SEPAS = [
    "gomory",
    "cmir",
    "clique",
    "flowcover",
    "zerohalf",
    "strongcg",
    "aggregation",
    "impliedbounds",
]


def cfg_vector(**on: int) -> Dict[str, int]:
    """Return a full config dict over SEPAS, defaulting to 0 unless specified."""
    d = {s: 0 for s in SEPAS}
    for k, v in on.items():
        if k not in d:
            raise ValueError(f"Unknown sepa '{k}' in cfg_vector")
        d[k] = int(v)
    return d


CONFIGS: List[Dict[str, Any]] = [
    {
        "config_id": 0,
        "name": "all_on",
        "sepa_freq": {s: 1 for s in SEPAS},
    },
    {
        "config_id": 1,
        "name": "all_off",
        "sepa_freq": {s: 0 for s in SEPAS},
    },
    {
        "config_id": 2,
        "name": "gomory_cmir",
        "sepa_freq": cfg_vector(gomory=1, cmir=1),
    },
    {
        "config_id": 3,
        "name": "clique_only",
        "sepa_freq": cfg_vector(clique=1),
    },
    {
        "config_id": 4,
        "name": "flowcover_only",
        "sepa_freq": cfg_vector(flowcover=1),
    },
    {
        "config_id": 5,
        "name": "zerohalf_only",
        "sepa_freq": cfg_vector(zerohalf=1),
    },
    {
        "config_id": 6,
        "name": "strongcg_only",
        "sepa_freq": cfg_vector(strongcg=1),
    },
    {
        "config_id": 7,
        "name": "impliedbounds_only",
        "sepa_freq": cfg_vector(impliedbounds=1),
    },
    {
        "config_id": 8,
        "name": "mix_balanced",
        "sepa_freq": cfg_vector(clique=1, flowcover=1, impliedbounds=1, aggregation=1),
    },
    {
        "config_id": 9,
        "name": "mix_aggressive",
        "sepa_freq": cfg_vector(gomory=1, cmir=1, strongcg=1, zerohalf=1),
    },
]


# -----------------------------
# Helpers
# -----------------------------

def windows_to_wsl_path(p: str) -> str:
    """
    Convert 'C:\\Users\\...' to '/mnt/c/Users/...' if needed.
    If it's already a POSIX path, return unchanged.
    """
    if ":" in p and "\\" in p:
        drive = p[0].lower()
        rest = p[2:].replace("\\", "/").lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return p


def set_sepa_freqs(m: Model, sepa_freq: Dict[str, int]) -> None:
    """
    Enable/disable separators by setting separating/<sepa>/freq.
    freq=0 disables, freq=1 enables (run each round as default dictates).
    """
    for sepa, freq in sepa_freq.items():
        param = f"separating/{sepa}/freq"
        try:
            m.setIntParam(param, int(freq))
        except Exception as e:
            raise RuntimeError(f"Failed to set {param}={freq}: {e}") from e


def run_one(lp_path: str,
            sepa_freq: Dict[str, int],
            time_limit: int,
            node_limit: Optional[int],
            maxroundsroot: int,
            maxrounds: int,
            hide_output: bool = True) -> Dict[str, Any]:
    """
    Solve one instance under one config; return metrics including solve time.
    """
    m = Model()
    if hide_output:
        m.hideOutput(True)

    # Basic limits
    m.setRealParam("limits/time", float(time_limit))
    if node_limit is not None:
        # limits/nodes is Longint in some builds; use setLongintParam if available.
        try:
            m.setLongintParam("limits/nodes", int(node_limit))
        except Exception:
            # fallback: just skip if not supported
            pass

    # Separation rounds cap (keeps experiments comparable / cheaper)
    m.setIntParam("separating/maxroundsroot", int(maxroundsroot))
    m.setIntParam("separating/maxrounds", int(maxrounds))

    # Apply config
    set_sepa_freqs(m, sepa_freq)

    # Load and solve
    m.readProblem(lp_path)

    t0 = time.time()
    m.optimize()
    wall = time.time() - t0

    # Metrics
    out: Dict[str, Any] = {
        "solve_time_sec": float(getattr(m, "getSolvingTime", lambda: wall)()),
        "wall_time_sec": float(wall),
    }

    # Status / objective / nodes if available
    try:
        out["status"] = str(m.getStatus())
    except Exception:
        out["status"] = None

    try:
        out["obj"] = float(m.getObjVal())
    except Exception:
        out["obj"] = None

    try:
        out["nodes"] = int(m.getNNodes())
    except Exception:
        out["nodes"] = None

    try:
        out["lp_iterations"] = int(m.getNLPIterations())
    except Exception:
        out["lp_iterations"] = None

    return out


# -----------------------------
# Main
# -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to manifest.json (Windows or WSL path ok)")
    ap.add_argument("--outdir", default="outputs_step3_collect_time", help="Output folder")
    ap.add_argument("--time-limit", type=int, default=300, help="SCIP time limit per run (sec)")
    ap.add_argument("--node-limit", type=int, default=None, help="Optional node limit per run")
    ap.add_argument("--maxroundsroot", type=int, default=10, help="SCIP separating/maxroundsroot")
    ap.add_argument("--maxrounds", type=int, default=10, help="SCIP separating/maxrounds")
    ap.add_argument("--seed", type=int, default=0, help="Not used heavily yet; reserved for shuffling/order")
    ap.add_argument("--max-instances", type=int, default=None, help="Optional cap for quick debugging")
    args = ap.parse_args()

    manifest_path = Path(windows_to_wsl_path(args.manifest))
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Save configs
    with open(outdir / "configs.json", "w") as f:
        json.dump(CONFIGS, f, indent=2)

    # Load manifest entries
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Instances live in the same directory as manifest (your generator wrote relative names)
    inst_dir = manifest_path.parent

    if args.max_instances is not None:
        manifest = manifest[: int(args.max_instances)]

    # Output files
    csv_path = outdir / "results.csv"
    jsonl_path = outdir / "results.jsonl"

    fieldnames = [
        "instance_name",
        "case",
        "config_id",
        "config_name",
        "lp_path",
        "sidecar_path",
        "solve_time_sec",
        "wall_time_sec",
        "status",
        "obj",
        "nodes",
        "lp_iterations",
        "time_limit",
        "maxroundsroot",
        "maxrounds",
    ]

    # Write headers
    write_header = not csv_path.exists()
    with open(csv_path, "a", newline="") as fcsv, open(jsonl_path, "a") as fjsonl:
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        total_runs = 0
        for entry in manifest:
            lp_rel = entry["lp"]
            side_rel = entry["sidecar"]
            case = entry.get("case", None)

            lp_path = str(inst_dir / lp_rel)
            sidecar_path = str(inst_dir / side_rel)

            instance_name = Path(lp_rel).stem  # filename w/out .lp

            if not Path(lp_path).exists():
                print(f"[WARN] missing lp: {lp_path}, skipping")
                continue

            for cfg in CONFIGS:
                cfg_id = cfg["config_id"]
                cfg_name = cfg["name"]
                sepa_freq = cfg["sepa_freq"]

                print(f"[RUN] {instance_name} | {cfg_name}")
                metrics = run_one(
                    lp_path=lp_path,
                    sepa_freq=sepa_freq,
                    time_limit=args.time_limit,
                    node_limit=args.node_limit,
                    maxroundsroot=args.maxroundsroot,
                    maxrounds=args.maxrounds,
                    hide_output=True,
                )

                row = {
                    "instance_name": instance_name,
                    "case": case,
                    "config_id": cfg_id,
                    "config_name": cfg_name,
                    "lp_path": lp_path,
                    "sidecar_path": sidecar_path,
                    "solve_time_sec": metrics.get("solve_time_sec"),
                    "wall_time_sec": metrics.get("wall_time_sec"),
                    "status": metrics.get("status"),
                    "obj": metrics.get("obj"),
                    "nodes": metrics.get("nodes"),
                    "lp_iterations": metrics.get("lp_iterations"),
                    "time_limit": args.time_limit,
                    "maxroundsroot": args.maxroundsroot,
                    "maxrounds": args.maxrounds,
                }

                writer.writerow(row)
                fcsv.flush()

                fjsonl.write(json.dumps({**row, "sepa_freq": sepa_freq}) + "\n")
                fjsonl.flush()

                total_runs += 1

        print(f"\nDone. Wrote {total_runs} runs to:")
        print(f"  {csv_path}")
        print(f"  {jsonl_path}")
        print(f"  {outdir / 'configs.json'}")


if __name__ == "__main__":
    main()
