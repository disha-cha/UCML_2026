#!/usr/bin/env python
"""
generate_uc_instances.py

Stochastic (2-stage) copper-plate UC instance generator for L2Sep experiments.

Key properties (correct UC, no fake transmission):
- First-stage binaries shared across scenarios: u, v, w
- Second-stage dispatch/reserve per scenario: p, r
- Correct startup/shutdown transition with initial conditions u0, p0
- Correct min up/down using robust "windowed-on/off" constraints
- Correct reserve coupling: p + r <= Pmax * u
- Ramp constraints include t=1 using initial p0
- Optional feasibility-screen solve (if a MILP solver is available locally)
- Dataset mode that regenerates until slack is ~0 (load shed/reserve short)

Outputs:
- LP file
- .minud.json sidecar with UC-specific metadata (+ feasibility + slack_summary if screened)

NOTE:
- This file uses pandapower only for network sizing + load distribution, but the UC model
  is copper-plate (no PTDF/angles/zones). Do not claim SCUC.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

import numpy as np
import pyomo.environ as pyo

try:
    import pandapower as pp
except Exception as e:
    raise ImportError(
        "pandapower is required for this generator (network sizing + load distribution). "
        "Install pandapower in your environment."
    ) from e


# -----------------------------------------------------------------------------
# Network Loading
# -----------------------------------------------------------------------------

NETWORK_LOADERS = {
    "case5": pp.networks.case5,
    "case9": pp.networks.case9,
    "case14": pp.networks.case14,
    "case30": pp.networks.case30,
    "case57": pp.networks.case57,
    "case118": pp.networks.case118,
    "case300": pp.networks.case300,
    "case1354pegase": pp.networks.case1354pegase,
}


def load_network(case_name: str):
    if case_name not in NETWORK_LOADERS:
        raise ValueError(f"Unknown case: {case_name}. Available: {list(NETWORK_LOADERS.keys())}")
    return NETWORK_LOADERS[case_name]()


# -----------------------------------------------------------------------------
# Data Generation
# -----------------------------------------------------------------------------

def generate_uc_data(
    net,
    n_scenarios: int = 10,
    time_periods: int = 24,
    seed: Optional[int] = None,
    demand_std: float = 0.10,
    reserve_fraction: float = 0.12,
    target_utilization: float = 0.55,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Generate UC problem data from a pandapower network.

    Returns:
      (pyomo_data, metadata)
      where pyomo_data is {None: param_dict} for AbstractModel.create_instance()
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # "Thermal generators" proxy
    if hasattr(net, "gen") and len(net.gen) > 0:
        thermal_gens = net.gen.reset_index(drop=True)
    elif hasattr(net, "ext_grid") and len(net.ext_grid) > 0:
        thermal_gens = net.ext_grid.reset_index(drop=True)
    else:
        raise ValueError("No generators found in network (net.gen or net.ext_grid).")

    n_gen = len(thermal_gens)
    n_buses = len(net.bus)

    G = range(1, n_gen + 1)
    T = range(1, time_periods + 1)
    N = range(1, n_buses + 1)
    S = range(1, n_scenarios + 1)

    p: Dict[str, Any] = {}

    # ---- Generator parameters ----
    gen_types = {g: random.choice(["coal", "ccgt"]) for g in G}

    p["OpEx"] = {
        g: random.uniform(35, 45) if gen_types[g] == "coal" else random.uniform(25, 35)
        for g in G
    }

    # Capacities (synthetic if missing)
    if hasattr(thermal_gens, "columns") and "max_p_mw" in thermal_gens.columns:
        Pmax = {g: max(float(thermal_gens.at[g - 1, "max_p_mw"]), 10.0) for g in G}
    elif hasattr(thermal_gens, "columns") and "p_mw" in thermal_gens.columns:
        Pmax = {g: max(1.5 * float(thermal_gens.at[g - 1, "p_mw"]), 10.0) for g in G}
    else:
        Pmax = {g: random.uniform(80, 250) for g in G}

    Pmin = {g: 0.2 * Pmax[g] for g in G}
    total_capacity = float(sum(Pmax.values()))

    p["Pmax"] = Pmax
    p["Pmin"] = Pmin
    p["Pramp"] = {g: 0.4 * Pmax[g] for g in G}
    p["Rmax"] = {g: 0.5 * Pmax[g] for g in G}

    p["Csu"] = {g: random.uniform(1000, 3000) for g in G}
    p["Csd"] = {g: 0.5 * p["Csu"][g] for g in G}

    # Min up/down
    p["Ton"] = {g: random.randint(3, 6) for g in G}
    p["Toff"] = {g: random.randint(3, 6) for g in G}

    # ---- Initial conditions (reduces early-hour ramp infeasibility) ----
    sorted_g = sorted(G, key=lambda g: Pmax[g], reverse=True)
    typical_load = target_utilization * total_capacity * 0.9

    u0 = {g: 0 for g in G}
    p0 = {g: 0.0 for g in G}

    cap_online = 0.0
    for g in sorted_g:
        if cap_online < typical_load:
            u0[g] = 1
            p0[g] = float(Pmin[g])  # safe initial dispatch
            cap_online += float(Pmax[g])
        else:
            break

    p["u0"] = u0
    p["p0"] = p0

    # ---- Demand scenarios ----
    bus_load_base = {n: 0.0 for n in N}
    if hasattr(net, "load") and len(net.load) > 0:
        for _, row in net.load.iterrows():
            bus_idx = int(row["bus"]) + 1  # 1-index
            bus_load_base[bus_idx] += float(row.get("p_mw", 0.0))

    total_base_load = float(sum(bus_load_base.values()))
    if total_base_load < 1e-6:
        # fallback: distribute across all buses
        for n in N:
            bus_load_base[n] = 1.0
        total_base_load = float(sum(bus_load_base.values()))

    # scale to target utilization
    target_load = target_utilization * total_capacity
    scale = target_load / max(total_base_load, 1e-6)
    for n in N:
        bus_load_base[n] *= scale

    # pattern that starts low; peaks later
    raw = np.sin(np.linspace(-np.pi / 2, 3 * np.pi / 2, time_periods))  # starts low
    time_pattern = 0.65 + 0.45 * (raw + 1) / 2  # in [0.65, 1.10]

    p["D"] = {}
    p["Prob"] = {}
    p["Pre"] = {}

    demand_by_time: List[float] = []
    for s in S:
        p["Prob"][s] = 1.0 / n_scenarios
        for t in T:
            total_t = 0.0
            for n in N:
                base = bus_load_base[n] * float(time_pattern[t - 1])
                noise = float(np.clip(np.random.normal(1.0, demand_std), 0.85, 1.15))
                d = max(base * noise, 0.0)
                p["D"][(s, t, n)] = float(d)
                total_t += float(d)
            p["Pre"][(s, t)] = float(reserve_fraction * total_t)

    for t in T:
        expected_t = sum(p["D"][(s, t, n)] * p["Prob"][s] for s in S for n in N)
        demand_by_time.append(float(expected_t))

    reserve_by_time = [float(sum(p["Pre"][(s, t)] * p["Prob"][s] for s in S)) for t in T]

    metadata = {
        "Lup": {str(g): int(p["Ton"][g]) for g in G},
        "Ldown": {str(g): int(p["Toff"][g]) for g in G},
        "Pmin": {str(g): float(Pmin[g]) for g in G},
        "Pmax": {str(g): float(Pmax[g]) for g in G},
        "Demand": demand_by_time,
        "Reserve": reserve_by_time,
        "times": list(T),
        "buses": list(N),
        "n_scenarios": n_scenarios,
        "n_generators": n_gen,
        "total_capacity": total_capacity,
        "note": "Copper-plate stochastic UC (no enforceable transmission constraints).",
    }

    return {None: p}, metadata


# -----------------------------------------------------------------------------
# Correct Copper-Plate Stochastic UC Model
# -----------------------------------------------------------------------------

def build_uc_model(n_gen: int, n_buses: int, time_periods: int, n_scenarios: int):
    from pyomo.environ import (
        AbstractModel, Set, RangeSet, Param, Var, Constraint, Objective,
        NonNegativeReals, Binary, minimize
    )

    m = AbstractModel("Stochastic_CopperPlate_UC")

    # Sets
    m.G = Set(initialize=range(1, n_gen + 1))
    m.T = RangeSet(1, time_periods)
    m.N = RangeSet(1, n_buses)
    m.S = RangeSet(1, n_scenarios)

    # Parameters
    m.OpEx = Param(m.G)
    m.Csu = Param(m.G)
    m.Csd = Param(m.G)

    m.Pmin = Param(m.G)
    m.Pmax = Param(m.G)
    m.Pramp = Param(m.G)
    m.Rmax = Param(m.G)

    m.Ton = Param(m.G)
    m.Toff = Param(m.G)

    m.D = Param(m.S, m.T, m.N, default=0.0)
    m.Prob = Param(m.S)
    m.Pre = Param(m.S, m.T, default=0.0)

    # Initial conditions
    m.u0 = Param(m.G, within=Binary, default=0)
    m.p0 = Param(m.G, default=0.0)

    # Variables
    m.u = Var(m.G, m.T, within=Binary)  # on/off
    m.v = Var(m.G, m.T, within=Binary)  # startup
    m.w = Var(m.G, m.T, within=Binary)  # shutdown

    m.p = Var(m.G, m.T, m.S, within=NonNegativeReals)  # dispatch
    m.r = Var(m.G, m.T, m.S, within=NonNegativeReals)  # reserve

    # Slack variables (penalized heavily; used for filtering)
    m.load_shed = Var(m.S, m.T, within=NonNegativeReals)  # unmet demand
    m.spill = Var(m.S, m.T, within=NonNegativeReals)      # dumped generation
    m.res_short = Var(m.S, m.T, within=NonNegativeReals)  # reserve shortfall

    # (1) Generation bounds
    def gen_min_rule(m, g, t, s):
        return m.Pmin[g] * m.u[g, t] <= m.p[g, t, s]
    m.gen_min = Constraint(m.G, m.T, m.S, rule=gen_min_rule)

    def gen_max_rule(m, g, t, s):
        return m.p[g, t, s] <= m.Pmax[g] * m.u[g, t]
    m.gen_max = Constraint(m.G, m.T, m.S, rule=gen_max_rule)

    # (2) Reserve coupling
    def gen_reserve_joint_rule(m, g, t, s):
        return m.p[g, t, s] + m.r[g, t, s] <= m.Pmax[g] * m.u[g, t]
    m.gen_reserve_joint = Constraint(m.G, m.T, m.S, rule=gen_reserve_joint_rule)

    def unit_reserve_cap_rule(m, g, t, s):
        return m.r[g, t, s] <= m.Rmax[g] * m.u[g, t]
    m.unit_reserve_cap = Constraint(m.G, m.T, m.S, rule=unit_reserve_cap_rule)

    def system_reserve_rule(m, s, t):
        return sum(m.r[g, t, s] for g in m.G) + m.res_short[s, t] >= m.Pre[s, t]
    m.system_reserve = Constraint(m.S, m.T, rule=system_reserve_rule)

    # (3) Copper-plate power balance
    def power_balance_rule(m, s, t):
        demand = sum(m.D[s, t, n] for n in m.N)
        return sum(m.p[g, t, s] for g in m.G) + m.load_shed[s, t] == demand + m.spill[s, t]
    m.power_balance = Constraint(m.S, m.T, rule=power_balance_rule)

    # (4) Ramp constraints (include t=1 using p0)
    def ramp_up_rule(m, g, t, s):
        if t == m.T.first():
            return m.p[g, t, s] - m.p0[g] <= m.Pramp[g]
        return m.p[g, t, s] - m.p[g, t - 1, s] <= m.Pramp[g]
    m.ramp_up = Constraint(m.G, m.T, m.S, rule=ramp_up_rule)

    def ramp_down_rule(m, g, t, s):
        if t == m.T.first():
            return m.p0[g] - m.p[g, t, s] <= m.Pramp[g]
        return m.p[g, t - 1, s] - m.p[g, t, s] <= m.Pramp[g]
    m.ramp_down = Constraint(m.G, m.T, m.S, rule=ramp_down_rule)

    # (5) Commitment transitions with initial u0
    def commit_transition_rule(m, g, t):
        if t == m.T.first():
            return m.u[g, t] - m.u0[g] == m.v[g, t] - m.w[g, t]
        return m.u[g, t] - m.u[g, t - 1] == m.v[g, t] - m.w[g, t]
    m.commit_transition = Constraint(m.G, m.T, rule=commit_transition_rule)

    # (6) Tightening inequalities for v,w
    def startup_upper1(m, g, t):
        return m.v[g, t] <= m.u[g, t]
    m.startup_upper1 = Constraint(m.G, m.T, rule=startup_upper1)

    def startup_upper2(m, g, t):
        if t == m.T.first():
            return m.v[g, t] <= 1 - m.u0[g]
        return m.v[g, t] <= 1 - m.u[g, t - 1]
    m.startup_upper2 = Constraint(m.G, m.T, rule=startup_upper2)

    def shutdown_upper1(m, g, t):
        if t == m.T.first():
            return m.w[g, t] <= m.u0[g]
        return m.w[g, t] <= m.u[g, t - 1]
    m.shutdown_upper1 = Constraint(m.G, m.T, rule=shutdown_upper1)

    def shutdown_upper2(m, g, t):
        return m.w[g, t] <= 1 - m.u[g, t]
    m.shutdown_upper2 = Constraint(m.G, m.T, rule=shutdown_upper2)

    # (7) Min up/down time constraints (horizon-safe)
    def min_up_rule(m, g, t):
        L = int(m.Ton[g])
        if L <= 1:
            return Constraint.Skip
        t_last = min(m.T.last(), t + L - 1)
        window_len = t_last - t + 1
        return sum(m.u[g, tau] for tau in range(t, t_last + 1)) >= window_len * m.v[g, t]
    m.min_up = Constraint(m.G, m.T, rule=min_up_rule)

    def min_down_rule(m, g, t):
        L = int(m.Toff[g])
        if L <= 1:
            return Constraint.Skip
        t_last = min(m.T.last(), t + L - 1)
        window_len = t_last - t + 1
        return sum(1 - m.u[g, tau] for tau in range(t, t_last + 1)) >= window_len * m.w[g, t]
    m.min_down = Constraint(m.G, m.T, rule=min_down_rule)

    # Objective (penalize slack heavily so "good" instances use ~0 slack)
    def total_cost_rule(m):
        op_cost = sum(m.Prob[s] * m.OpEx[g] * m.p[g, t, s] for s in m.S for g in m.G for t in m.T)
        commit_cost = sum(m.Csu[g] * m.v[g, t] + m.Csd[g] * m.w[g, t] for g in m.G for t in m.T)

        VOLL = 1e6       # value of lost load
        SPILL_PEN = 1e3  # discourage dumping but far less than shedding
        RES_SHORT = 1e5  # reserve shortfall penalty

        slack_cost = sum(
            m.Prob[s] * (VOLL * m.load_shed[s, t] + SPILL_PEN * m.spill[s, t] + RES_SHORT * m.res_short[s, t])
            for s in m.S for t in m.T
        )
        return op_cost + commit_cost + slack_cost

    m.obj = Objective(rule=total_cost_rule, sense=minimize)
    return m


# -----------------------------------------------------------------------------
# Solve Helpers
# -----------------------------------------------------------------------------

def try_solve_feasibility(instance: pyo.ConcreteModel, time_limit_s: int = 30) -> Optional[Dict[str, Any]]:
    """
    Try to solve the instance if a solver is available.

    Prefers: scip, gurobi, cbc, highs, glpk.
    IMPORTANT: We do NOT require optimality for screening; we mainly want a feasible incumbent.
    """
    candidates = ["scip", "gurobi", "cbc", "highs", "glpk"]
    for name in candidates:
        try:
            solver = pyo.SolverFactory(name)
            if solver is None or not solver.available():
                continue

            try:
                if name == "scip":
                    solver.options["limits/time"] = time_limit_s
                elif name == "gurobi":
                    solver.options["TimeLimit"] = time_limit_s
                elif name == "cbc":
                    solver.options["seconds"] = time_limit_s
                elif name == "highs":
                    solver.options["time_limit"] = time_limit_s
                elif name == "glpk":
                    solver.options["tmlim"] = time_limit_s
            except Exception:
                pass

            res = solver.solve(instance, tee=False)
            term = str(res.solver.termination_condition)
            status = str(res.solver.status)
            return {"solver": name, "status": status, "termination": term}
        except Exception:
            continue
    return None


def _safe_value(x) -> Optional[float]:
    """Return float value of a Pyomo expression/var, or None if unavailable."""
    try:
        v = pyo.value(x)
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Instance Generation
# -----------------------------------------------------------------------------

def generate_instance(
    case_name: str,
    n_scenarios: int = 10,
    time_periods: int = 24,
    seed: Optional[int] = None,
    out_dir: str = "instances",
    screen_feasibility: bool = False,
    screen_time_limit_s: int = 60,
) -> Tuple[str, str]:
    net = load_network(case_name)

    # sizes
    if hasattr(net, "gen") and len(net.gen) > 0:
        n_gen = len(net.gen)
    else:
        n_gen = len(net.ext_grid)
    n_buses = len(net.bus)

    pyomo_data, metadata = generate_uc_data(
        net,
        n_scenarios=n_scenarios,
        time_periods=time_periods,
        seed=seed,
    )

    abstract_model = build_uc_model(n_gen, n_buses, time_periods, n_scenarios)
    instance = abstract_model.create_instance(pyomo_data)

    # Optional feasibility screen (records slack even if time-limited)
    solve_info = None
    if screen_feasibility:
        solve_info = try_solve_feasibility(instance, time_limit_s=screen_time_limit_s)
        metadata["feasibility_screen"] = solve_info or {"note": "No solver available / not solved."}

        metadata["has_solution"] = False
        vals_present = True
        total_shed = 0.0
        total_spill = 0.0
        total_res_short = 0.0

        if solve_info is not None and solve_info.get("status") in ("ok", "warning"):
            for s in instance.S:
                for t in instance.T:
                    v1 = _safe_value(instance.load_shed[s, t])
                    v2 = _safe_value(instance.spill[s, t])
                    v3 = _safe_value(instance.res_short[s, t])
                    if v1 is None or v2 is None or v3 is None:
                        vals_present = False
                        break
                    total_shed += v1
                    total_spill += v2
                    total_res_short += v3
                if not vals_present:
                    break
        else:
            vals_present = False

        if vals_present:
            metadata["has_solution"] = True
            metadata["slack_summary"] = {
                "load_shed": float(total_shed),
                "spill": float(total_spill),
                "reserve_short": float(total_res_short),
            }
            print("Slack diagnostics:")
            print("  Load shed:", total_shed)
            print("  Spill:", total_spill)
            print("  Reserve short:", total_res_short)
        else:
            metadata["slack_summary_note"] = (
                "No incumbent values available (solver may have timed out before finding feasible solution)."
            )

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    seed_str = f"_seed{seed}" if seed is not None else ""
    filename = f"{case_name}_S{n_scenarios}_T{time_periods}{seed_str}"

    lp_path = out_path / f"{filename}.lp"
    sidecar_path = out_path / f"{filename}.minud.json"

    instance.write(str(lp_path))
    with open(sidecar_path, "w") as f:
        json.dump(metadata, f, indent=2)

    n_vars = sum(1 for _ in instance.component_data_objects(pyo.Var))
    n_cons = sum(1 for _ in instance.component_data_objects(pyo.Constraint))

    print(f"Generated: {lp_path.name}")
    print(f"  Variables: {n_vars}, Constraints: {n_cons}")
    print(f"  Generators: {n_gen}, Buses: {n_buses}")
    print(f"  Scenarios: {n_scenarios}, Time periods: {time_periods}")
    if screen_feasibility:
        print(f"  Feasibility screen: {solve_info}")

    return str(lp_path), str(sidecar_path)


def generate_dataset(
    cases: List[str],
    out_dir: str,
    n_per_case: int,
    scenarios: int,
    time_periods: int,
    screen_time_limit_s: int,
    eps: float = 1e-6,
    max_attempts_factor: int = 50,
) -> None:
    """
    Generate a dataset and keep only "clean" instances:
      abs(load_shed) <= eps and abs(reserve_short) <= eps

    Uses screening solve but does NOT require proven optimality.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    def clamp0(x: float, tol: float = 1e-9) -> float:
        return 0.0 if abs(x) <= tol else x

    manifest: List[Dict[str, Any]] = []
    for case in cases:
        accepted = 0
        attempts = 0
        max_attempts = max_attempts_factor * n_per_case

        print(f"\n=== {case}: generating {n_per_case} clean instances ===")
        while accepted < n_per_case:
            attempts += 1
            if attempts > max_attempts:
                raise RuntimeError(
                    f"Too many attempts for {case}. "
                    f"Try increasing --screen-time-limit or reducing scenarios/time-periods."
                )

            seed = accepted * 100000 + attempts
            print(f"\n[{case}] attempt {attempts} (accepted {accepted}/{n_per_case}), seed={seed}")

            lp, sidecar = generate_instance(
                case_name=case,
                n_scenarios=scenarios,
                time_periods=time_periods,
                seed=seed,
                out_dir=out_dir,
                screen_feasibility=True,
                screen_time_limit_s=screen_time_limit_s,
            )

            # Read slack summary from sidecar to decide keep/reject
            with open(sidecar, "r") as f:
                meta = json.load(f)

            slack = meta.get("slack_summary", None)
            if slack is None:
                print("  ❌ rejected (missing slack_summary; no readable incumbent recorded)")
                try:
                    Path(lp).unlink(missing_ok=True)
                    Path(sidecar).unlink(missing_ok=True)
                except Exception:
                    pass
                continue

            shed = clamp0(float(slack.get("load_shed", 1e99)))
            rshort = clamp0(float(slack.get("reserve_short", 1e99)))

            if abs(shed) <= eps and abs(rshort) <= eps:
                print(f"  ✅ accepted (shed={shed:.3e}, rshort={rshort:.3e})")
                manifest.append({
                    "case": case,
                    "lp": Path(lp).name,
                    "sidecar": Path(sidecar).name,
                    "seed": seed,
                    "scenarios": scenarios,
                    "time_periods": time_periods,
                })
                accepted += 1
            else:
                print(f"  ❌ rejected (shed={shed:.3e}, rshort={rshort:.3e})")
                try:
                    Path(lp).unlink(missing_ok=True)
                    Path(sidecar).unlink(missing_ok=True)
                except Exception:
                    pass

    manifest_path = out_path / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved to {manifest_path}")
    print(f"Total accepted instances: {len(manifest)}")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate copper-plate stochastic UC instances for L2Sep")

    parser.add_argument("--case", type=str, help="Case name (e.g., case118)")
    parser.add_argument("--scenarios", type=int, default=10, help="Number of scenarios")
    parser.add_argument("--time-periods", type=int, default=24, help="Time periods")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--out-dir", default="instances", help="Output directory")

    parser.add_argument(
        "--screen-feasibility",
        action="store_true",
        help="Try to solve each instance with an available MILP solver (SCIP/Gurobi/etc).",
    )
    parser.add_argument(
        "--screen-time-limit",
        type=int,
        default=60,
        help="Time limit (seconds) for feasibility screen solve.",
    )

    # Dataset mode
    parser.add_argument("--dataset", action="store_true", help="Generate a dataset with automatic accept/reject.")
    parser.add_argument("--cases", nargs="+", default=["case57", "case118", "case300"], help="Cases in dataset mode.")
    parser.add_argument("--n-per-case", type=int, default=10, help="Accepted instances per case in dataset mode.")
    parser.add_argument("--eps", type=float, default=1e-6, help="Slack tolerance for acceptance.")
    parser.add_argument("--max-attempts-factor", type=int, default=50, help="Max attempts = factor * n-per-case.")

    args = parser.parse_args()

    if args.dataset:
        generate_dataset(
            cases=args.cases,
            out_dir=args.out_dir,
            n_per_case=args.n_per_case,
            scenarios=args.scenarios,
            time_periods=args.time_periods,
            screen_time_limit_s=args.screen_time_limit,
            eps=args.eps,
            max_attempts_factor=args.max_attempts_factor,
        )
        return

    if not args.case:
        parser.print_help()
        print("\nExamples:")
        print("  python generate_uc_instances.py --case case118 --scenarios 5 --time-periods 24 --seed 1 --screen-feasibility --screen-time-limit 60")
        print("  python generate_uc_instances.py --dataset --cases case57 case118 case300 --n-per-case 60 --scenarios 5 --time-periods 24 --screen-time-limit 60")
        return

    generate_instance(
        case_name=args.case,
        n_scenarios=args.scenarios,
        time_periods=args.time_periods,
        seed=args.seed,
        out_dir=args.out_dir,
        screen_feasibility=args.screen_feasibility,
        screen_time_limit_s=args.screen_time_limit,
    )


if __name__ == "__main__":
    main()
