#!/usr/bin/env python3
"""
build_subset_A.py

Build restricted configuration subset A using greedy ERM-style selection,
based on measured solve times in results.jsonl.

We define delta(s,x) relative to baseline config (default: "all_on"):
    delta = (t_base - t_s) / t_base

Outputs:
  outputs_step4_restrict_space/A.json
  outputs_step4_restrict_space/delta_matrix.csv
  outputs_step4_restrict_space/summary.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def greedy_select(delta_df: pd.DataFrame, candidates: list[str], max_k: int) -> tuple[list[str], list[float]]:
    """
    delta_df: index=instance_name, columns=config_name, values=delta
    candidates: candidate config names
    """
    A: list[str] = []
    curve: list[float] = []

    current_best = pd.Series(0.0, index=delta_df.index)  # best delta so far per instance
    for _ in range(max_k):
        best_c = None
        best_perf = None
        best_new_best = None

        for c in candidates:
            new_best = np.maximum(current_best.values, delta_df[c].values)
            perf = float(np.mean(new_best))
            if (best_perf is None) or (perf > best_perf + 1e-12):
                best_perf = perf
                best_c = c
                best_new_best = new_best

        if best_c is None:
            break

        A.append(best_c)
        curve.append(float(best_perf))
        candidates = [c for c in candidates if c != best_c]
        current_best = pd.Series(best_new_best, index=delta_df.index)

        if not candidates:
            break

    return A, curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-jsonl", required=True, help="Path to results.jsonl")
    ap.add_argument("--out-dir", default="outputs_step4_restrict_space", help="Output folder")
    ap.add_argument("--baseline", default="all_on", help="Baseline config_name")
    ap.add_argument("--min-avg-delta", type=float, default=0.0, help="Filter configs with avg delta < threshold")
    ap.add_argument("--max-A", type=int, default=5, help="Max size of A")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load results.jsonl
    records = []
    with open(args.results_jsonl, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    df = pd.DataFrame(records)

    # Expect these columns (from your collector)
    required = {"instance_name", "config_name", "solve_time_sec"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"results.jsonl missing columns: {missing}. Found: {list(df.columns)}")

    # Build baseline time per instance
    base = df[df["config_name"] == args.baseline].set_index("instance_name")["solve_time_sec"]
    if base.index.nunique() != df["instance_name"].nunique():
        # Some instances missing baseline; restrict to intersection
        common = sorted(set(df["instance_name"].unique()).intersection(set(base.index)))
        df = df[df["instance_name"].isin(common)].copy()
        base = base.loc[common]

    df["base_time"] = df["instance_name"].map(base)
    df["delta"] = (df["base_time"] - df["solve_time_sec"]) / df["base_time"]

    # Pivot to instance x config delta matrix
    delta_mat = df.pivot_table(
        index="instance_name",
        columns="config_name",
        values="delta",
        aggfunc="mean",
    )

    # Config statistics
    avg_delta = delta_mat.mean(axis=0).sort_values(ascending=False)

    # Candidate configs after filtering
    candidates = [c for c in delta_mat.columns if float(avg_delta.loc[c]) >= args.min_avg_delta]

    if len(candidates) == 0:
        raise RuntimeError("No configs survived filtering; lower --min-avg-delta.")

    # Greedy select A
    A, curve = greedy_select(delta_mat, candidates=candidates, max_k=args.max_A)

    # Save outputs
    delta_csv = out_dir / "delta_matrix.csv"
    delta_mat.to_csv(delta_csv)

    A_path = out_dir / "A.json"
    with open(A_path, "w") as f:
        json.dump(
            {
                "baseline": args.baseline,
                "min_avg_delta": args.min_avg_delta,
                "max_A": args.max_A,
                "A": A,
            },
            f,
            indent=2,
        )

    summary = {
        "n_instances": int(delta_mat.shape[0]),
        "configs_all": list(delta_mat.columns),
        "avg_delta": {k: float(v) for k, v in avg_delta.to_dict().items()},
        "A": A,
        "greedy_curve_mean_best_delta": curve,
        "mean_best_delta_A": float(delta_mat[A].max(axis=1).mean()) if A else 0.0,
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Wrote:")
    print(f"  {A_path}")
    print(f"  {delta_csv}")
    print(f"  {out_dir / 'summary.json'}")
    print("\nSelected A:")
    for i, c in enumerate(A, 1):
        print(f"  {i}. {c} (avg delta={avg_delta.loc[c]:.4f})")


if __name__ == "__main__":
    main()
