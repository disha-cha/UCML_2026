#!/usr/bin/env python3
"""
run_improved.py

Evaluate the improved solver strategies on UC instances.

Runs four solves per instance:
  1. all_on     — SCIP default (baseline)
  2. uc_branch  — UC-aware branching (commit vars first)
  3. cut_filter — Cut quality filtering (top-k cuts per round)
  4. combined   — UC-aware branching + cut quality filtering

Reports delta vs all_on for each strategy.

Usage:
  python src/run_improved.py \\
    --manifest data/instances_v3/manifest_val.json \\
    --outdir experiments/step7_improved_eval \\
    --n 20 \\
    --time-limit 300 \\
    --top-k 8

With trained cut ML model:
  python src/run_improved.py \\
    --manifest data/instances_v3/manifest_val.json \\
    --outdir experiments/step7_improved_eval \\
    --cut-model experiments/step7_cut_data/cut_model.pt \\
    --n 20 --time-limit 300 --top-k 8
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from pyscipopt import Model

from uc_branch import UCBranchrule, make_model_with_uc_branch
from cut_quality_sepa import CutQualitySepa, make_model_with_cut_filter


def solve_all_on(lp_path: str, time_limit: int) -> Dict[str, Any]:
    """SCIP default: all separators on."""
    m = Model()
    m.hideOutput(True)
    m.setRealParam("limits/time", float(time_limit))
    m.readProblem(lp_path)
    t0 = time.time()
    m.optimize()
    wall = time.time() - t0
    return _metrics(m, wall)


def solve_uc_branch(lp_path: str, time_limit: int, log: bool) -> Dict[str, Any]:
    """UC-aware branching, default cuts."""
    m, rule = make_model_with_uc_branch(lp_path, time_limit=time_limit, log=log)
    t0 = time.time()
    m.optimize()
    wall = time.time() - t0
    result = _metrics(m, wall)
    result["branch_stats"] = rule.get_stats()
    return result


def solve_cut_filter(
    lp_path: str,
    time_limit: int,
    top_k: int,
    cut_model: Optional[str],
    log: bool,
    top_frac: Optional[float] = None,
    min_keep: int = 5,
) -> Dict[str, Any]:
    """All cuts generated, but filter to top-k (or top-frac) per round."""
    m, sepa = make_model_with_cut_filter(
        lp_path,
        time_limit=time_limit,
        top_k=top_k,
        top_frac=top_frac,
        min_keep=min_keep,
        model_pt=cut_model,
        log=log,
    )
    t0 = time.time()
    m.optimize()
    wall = time.time() - t0
    result = _metrics(m, wall)
    result["cut_filter_stats"] = sepa.get_stats()
    return result


def solve_combined(
    lp_path: str,
    time_limit: int,
    top_k: int,
    cut_model: Optional[str],
    log: bool,
    top_frac: Optional[float] = None,
    min_keep: int = 5,
) -> Dict[str, Any]:
    """UC-aware branching + cut quality filtering."""
    m = Model()
    m.hideOutput(True)
    m.setRealParam("limits/time", float(time_limit))

    branch_rule = UCBranchrule(log=log)
    m.includeBranchrule(
        branch_rule,
        name="uc_commit_first",
        desc="UC commitment vars first",
        priority=100_000,
        maxdepth=-1,
        maxbounddist=1.0,
    )

    cut_sepa = CutQualitySepa(top_k=top_k, top_frac=top_frac, min_keep=min_keep,
                              model_pt=cut_model, log=log)
    m.includeSepa(
        cut_sepa,
        name="cut_quality_filter",
        desc="Top-k cut filtering",
        priority=-1,
        freq=1,
    )

    m.readProblem(lp_path)
    t0 = time.time()
    m.optimize()
    wall = time.time() - t0
    result = _metrics(m, wall)
    result["branch_stats"] = branch_rule.get_stats()
    result["cut_filter_stats"] = cut_sepa.get_stats()
    return result


def _metrics(m: Model, wall: float) -> Dict[str, Any]:
    try:
        solve_time = float(m.getSolvingTime())
    except Exception:
        solve_time = wall
    try:
        status = str(m.getStatus())
    except Exception:
        status = "unknown"
    try:
        obj = float(m.getObjVal())
    except Exception:
        obj = None
    try:
        nodes = int(m.getNNodes())
    except Exception:
        nodes = None
    return {
        "solve_time_sec": solve_time,
        "wall_time_sec": wall,
        "status": status,
        "obj": obj,
        "nodes": nodes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--time-limit", type=int, default=300)
    ap.add_argument("--top-k", type=int, default=8,
                    help="Fixed number of cuts to keep per round (used when --top-frac not set)")
    ap.add_argument("--top-frac", type=float, default=None,
                    help="Fraction of cuts to keep per round (e.g. 0.35). Overrides --top-k when set.")
    ap.add_argument("--min-keep", type=int, default=5,
                    help="Minimum cuts to keep when using --top-frac (floor)")
    ap.add_argument("--cut-model", default=None,
                    help="Trained cut quality MLP (.pt) — omit for heuristic mode")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()

    rng = np.random.RandomState(args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(args.manifest)
    inst_dir = manifest_path.parent
    with open(manifest_path) as f:
        manifest = json.load(f)
    rng.shuffle(manifest)
    manifest = manifest[:args.n]

    fieldnames = [
        "instance_name", "case",
        "t_allon", "t_branch", "t_cutfilter", "t_combined",
        "status_allon", "status_branch", "status_cutfilter", "status_combined",
        "nodes_allon", "nodes_branch", "nodes_cutfilter", "nodes_combined",
        "delta_branch", "delta_cutfilter", "delta_combined",
        "uc_branch_rate", "cut_keep_rate",
    ]

    rows = []
    csv_path = outdir / "results.csv"
    jsonl_path = outdir / "results.jsonl"

    with open(csv_path, "w", newline="") as fcsv:
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        writer.writeheader()

        for entry in manifest:
            lp_rel = entry["lp"]
            lp_path = str(inst_dir / lp_rel)
            inst_name = Path(lp_rel).stem
            case = entry.get("case", "")

            if not Path(lp_path).exists():
                print(f"[WARN] missing: {lp_path}")
                continue

            print(f"\n[{inst_name}]")

            r_on = solve_all_on(lp_path, args.time_limit)
            print(f"  all_on:     {r_on['solve_time_sec']:7.2f}s  "
                  f"[{r_on['status']}]  nodes={r_on['nodes']}")

            r_br = solve_uc_branch(lp_path, args.time_limit, args.log)
            print(f"  uc_branch:  {r_br['solve_time_sec']:7.2f}s  "
                  f"[{r_br['status']}]  nodes={r_br['nodes']}  "
                  f"uc_rate={r_br['branch_stats']['n_uc_branches']}/"
                  f"{r_br['branch_stats']['n_branches']}")

            r_cf = solve_cut_filter(lp_path, args.time_limit, args.top_k,
                                    args.cut_model, args.log, args.top_frac, args.min_keep)
            print(f"  cut_filter: {r_cf['solve_time_sec']:7.2f}s  "
                  f"[{r_cf['status']}]  nodes={r_cf['nodes']}  "
                  f"keep={r_cf['cut_filter_stats']['total_cuts_kept']}/"
                  f"{r_cf['cut_filter_stats']['total_cuts_seen']}")

            r_co = solve_combined(lp_path, args.time_limit, args.top_k,
                                  args.cut_model, args.log, args.top_frac, args.min_keep)
            print(f"  combined:   {r_co['solve_time_sec']:7.2f}s  "
                  f"[{r_co['status']}]  nodes={r_co['nodes']}")

            t_on = r_on["solve_time_sec"]
            denom = max(t_on, 1e-6)

            def delta(t_method):
                return round((t_on - t_method) / denom, 6)

            t_br = r_br["solve_time_sec"]
            t_cf = r_cf["solve_time_sec"]
            t_co = r_co["solve_time_sec"]

            d_br = delta(t_br)
            d_cf = delta(t_cf)
            d_co = delta(t_co)

            print(f"  Δ branch={d_br:+.4f}  Δ cut_filter={d_cf:+.4f}  Δ combined={d_co:+.4f}")

            # Branch rate
            bs = r_br["branch_stats"]
            uc_rate = (bs["n_uc_branches"] / max(bs["n_branches"], 1))

            # Cut keep rate (use combined stats)
            cs = r_co.get("cut_filter_stats", {})
            keep_rate = cs.get("keep_rate", float("nan"))

            row = {
                "instance_name": inst_name,
                "case": case,
                "t_allon": round(t_on, 4),
                "t_branch": round(t_br, 4),
                "t_cutfilter": round(t_cf, 4),
                "t_combined": round(t_co, 4),
                "status_allon": r_on["status"],
                "status_branch": r_br["status"],
                "status_cutfilter": r_cf["status"],
                "status_combined": r_co["status"],
                "nodes_allon": r_on["nodes"],
                "nodes_branch": r_br["nodes"],
                "nodes_cutfilter": r_cf["nodes"],
                "nodes_combined": r_co["nodes"],
                "delta_branch": d_br,
                "delta_cutfilter": d_cf,
                "delta_combined": d_co,
                "uc_branch_rate": round(uc_rate, 4),
                "cut_keep_rate": round(keep_rate, 4) if np.isfinite(keep_rate) else None,
            }
            rows.append(row)
            writer.writerow(row)
            fcsv.flush()

            with open(jsonl_path, "a") as fjsonl:
                fjsonl.write(json.dumps(row) + "\n")

    # Summary
    if rows:
        def summarize(col):
            vals = [r[col] for r in rows if r[col] is not None]
            arr = np.array(vals)
            return {
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "pct_positive": float((arr > 0).mean()),
            }

        summary = {
            "n": len(rows),
            "top_k": args.top_k,
            "cut_model": args.cut_model,
            "delta_branch": summarize("delta_branch"),
            "delta_cutfilter": summarize("delta_cutfilter"),
            "delta_combined": summarize("delta_combined"),
        }
        with open(outdir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        print("\n=== Summary ===")
        print(json.dumps(summary, indent=2))
    else:
        print("No results.")


if __name__ == "__main__":
    main()
