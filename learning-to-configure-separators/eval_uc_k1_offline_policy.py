#!/usr/bin/env python3
"""
eval_uc_k1_offline_policy.py

Step 5A: Offline evaluation of a trained k=1 policy using ONLY collected results.csv.
No SCIP re-solves; we just join predicted config -> observed solve time in results.csv.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import json

def _detect_cols(df: pd.DataFrame):
    cols = set(df.columns)

    # instance id column
    inst_candidates = [
        "instance_name", "instance", "instance_id", "case", "name",
        "lp_path", "mps_path", "problem"
    ]
    inst_col = next((c for c in inst_candidates if c in cols), None)
    if inst_col is None:
        raise RuntimeError(f"Could not find instance column. Have columns: {sorted(cols)}")

    # config name column
    cfg_candidates = ["config_name", "config", "config_id", "action", "arm", "policy"]
    cfg_col = next((c for c in cfg_candidates if c in cols), None)
    if cfg_col is None:
        raise RuntimeError(f"Could not find config column. Have columns: {sorted(cols)}")

    # time column (YOUR CSV HAS solve_time_sec / wall_time_sec)
    time_candidates = [
        "solve_time_sec", "wall_time_sec",
        "solve_time", "solving_time", "time", "seconds",
        "scip_time", "our_time"
    ]
    time_col = next((c for c in time_candidates if c in cols), None)
    if time_col is None:
        raise RuntimeError(f"Could not find time column. Have columns: {sorted(cols)}")

    # status column optional
    status_candidates = ["status", "scip_status", "result"]
    status_col = next((c for c in status_candidates if c in cols), None)

    return inst_col, cfg_col, time_col, status_col

def _normalize_inst(x: str) -> str:
    s = str(x).replace("\\", "/")
    # if it's a path, keep stem
    s = s.split("/")[-1]
    for suf in [".lp", ".mps", ".gz", ".json"]:
        if s.endswith(suf):
            s = s[: -len(suf)]
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-csv", required=True)
    ap.add_argument("--preds-csv", required=True)
    ap.add_argument("--baseline-config", default="all_off")
    ap.add_argument("--outdir", default="outputs_step5a_eval_k1_offline")
    ap.add_argument("--require-optimal", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    results = pd.read_csv(args.results_csv)
    preds = pd.read_csv(args.preds_csv)

    inst_col, cfg_col, time_col, status_col = _detect_cols(results)

    results["_inst"] = results[inst_col].map(_normalize_inst)
    results["_cfg"] = results[cfg_col].astype(str)

    if args.require_optimal and status_col is not None:
        st = results[status_col].astype(str).str.lower()
        keep = st.str.contains("optimal") | st.str.contains("solved") | st.str.contains("feasible")
        results = results[keep].copy()

    # preds csv: train_uc_k1_offline.py typically writes instance,pred_config,prob_*,true_best(optional)
    
    # --- preds csv column detection (supports multiple schemas) ---
    preds_cols = set(preds.columns)

# instance column
    pred_inst_col = None
    for c in ["instance", "instance_name", "case", "name"]:
    	if c in preds_cols:
        	pred_inst_col = c
        	break

# predicted config column
    pred_cfg_col = None
    for c in ["pred_config", "pred", "y_pred", "config_name", "action"]:
    	if c in preds_cols:
        	pred_cfg_col = c
        	break

    if pred_inst_col is None or pred_cfg_col is None:
    	raise RuntimeError(
        	f"preds CSV must contain instance + predicted-config columns. "
        	f"Have: {sorted(preds_cols)}"
    	)




    preds["_inst"] = preds[pred_inst_col].map(_normalize_inst)
    preds["_cfg_pred"] = preds[pred_cfg_col].astype(str)

    # Baseline times per instance
    base = results[results["_cfg"] == args.baseline_config][["_inst", time_col]].copy()
    base = base.rename(columns={time_col: "t_baseline"}).drop_duplicates(subset=["_inst"])

    # Predicted config times per instance
    merged = preds[["_inst", "_cfg_pred"]].merge(
        results[["_inst", "_cfg", time_col]],
        left_on=["_inst", "_cfg_pred"],
        right_on=["_inst", "_cfg"],
        how="left",
    ).rename(columns={time_col: "t_pred"}).drop(columns=["_cfg"])

    merged = merged.merge(base, on="_inst", how="left")

    merged["delta"] = (merged["t_baseline"] - merged["t_pred"]) / merged["t_baseline"]
    merged["delta"] = merged["delta"].replace([np.inf, -np.inf], np.nan)

    n_total = len(merged)
    n_ok = int(merged["t_pred"].notna().sum())
    summary = {
        "n_preds": int(n_total),
        "n_matched_to_results": n_ok,
        "match_rate": float(n_ok / max(1, n_total)),
        "baseline_config": args.baseline_config,
        "time_col_used": time_col,
        "mean_delta": float(np.nanmean(merged["delta"].values)),
        "median_delta": float(np.nanmedian(merged["delta"].values)),
        "pct_positive": float(np.nanmean((merged["delta"].values > 0).astype(float))),
    }

    merged.to_csv(outdir / "offline_policy_eval_rows.csv", index=False)
    with open(outdir / "offline_policy_eval_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Wrote:")
    print(f"  {outdir/'offline_policy_eval_rows.csv'}")
    print(f"  {outdir/'offline_policy_eval_summary.json'}")
    print("\nSummary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
