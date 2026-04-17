#!/usr/bin/env python3
"""
run_with_ucb.py

Solve UC instances using the UCB adaptive separator, optionally warm-started
from the offline-trained MLP classifier.

For each instance, runs three solves:
  1. baseline (all_off) — reference time
  2. all_on             — SCIP default cuts time
  3. ucb                — UCB adaptive separator time

Outputs:
  experiments/step6_ucb_eval/
    results.jsonl    -- per-instance metrics
    results.csv
    summary.json

Usage:
  python src/run_with_ucb.py \
    --manifest data/instances_v3/manifest.json \
    --uc-features-npz experiments/step2_features_v3/uc_features.npz \
    --lp-features-npz experiments/step2_features_v3/lp_features.npz \
    --model-pt experiments/step4_train_k1_v3/model.pt \
    --outdir experiments/step6_ucb_eval \
    --n 20 \
    --time-limit 300 \
    --alpha 1.0 \
    --max-rounds 10
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

from ucb_sepa import SEPAS, N_ARMS, LinUCB, UCBSepa, make_model_with_ucb, warm_start_from_offline_model


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def load_features_npz(path: str) -> Dict[str, np.ndarray]:
    """Load .npz feature file, return {instance_name: feature_vector}."""
    npz = np.load(path, allow_pickle=True)
    feats = npz["features"].astype(np.float32)
    names = [str(x) for x in npz["instance_names"].tolist()]
    return {n: feats[i] for i, n in enumerate(names)}


def solve_fixed_config(lp_path: str, all_on: bool, time_limit: int) -> Dict[str, Any]:
    """Solve with all separators on or all off. Returns metrics dict."""
    m = Model()
    m.hideOutput(True)
    m.setRealParam("limits/time", float(time_limit))
    for sepa in SEPAS:
        freq = 1 if all_on else 0
        try:
            m.setIntParam(f"separating/{sepa}/freq", freq)
        except Exception:
            pass
    m.readProblem(lp_path)
    t0 = time.time()
    m.optimize()
    wall = time.time() - t0
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
        "solve_time_sec": float(getattr(m, "getSolvingTime", lambda: wall)()),
        "wall_time_sec": wall,
        "status": status,
        "obj": obj,
        "nodes": nodes,
    }


def solve_with_ucb(
    lp_path: str,
    instance_feats: Optional[np.ndarray],
    warm_start_rewards: Optional[Dict[str, float]],
    time_limit: int,
    alpha: float,
    max_rounds: int,
    log: bool = False,
    time_limit_multiplier: float = 1.5,
    shared_ucb=None,
) -> Dict[str, Any]:
    """Solve with UCB adaptive separator. Returns metrics dict."""
    m, ucb_plugin = make_model_with_ucb(
        lp_path=lp_path,
        time_limit=time_limit,
        alpha=alpha,
        max_rounds=max_rounds,
        instance_feats=instance_feats,
        warm_start_rewards=warm_start_rewards,
        log=log,
        hide_output=True,
        time_limit_multiplier=time_limit_multiplier,
        shared_ucb=shared_ucb,
    )
    t0 = time.time()
    m.optimize()
    wall = time.time() - t0
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
        "solve_time_sec": float(getattr(m, "getSolvingTime", lambda: wall)()),
        "wall_time_sec": wall,
        "status": status,
        "obj": obj,
        "nodes": nodes,
        "ucb_round_log": ucb_plugin.get_log(),
        "n_ucb_rounds": len(ucb_plugin.get_log()),
    }


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--uc-features-npz", required=True)
    ap.add_argument("--lp-features-npz", default=None)
    ap.add_argument("--model-pt", default=None, help="Offline MLP for warm start")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--n", type=int, default=20, help="Number of instances to evaluate")
    ap.add_argument("--time-limit", type=int, default=300)
    ap.add_argument("--alpha", type=float, default=0.1, help="UCB exploration parameter")
    ap.add_argument("--max-rounds", type=int, default=10, help="Max separation rounds")
    ap.add_argument("--easy-threshold", type=float, default=60.0,
                    help="all_off solve time threshold (sec): instances faster than this use all_on fallback")
    ap.add_argument("--ucb-time-multiplier", type=float, default=1.5,
                    help="UCB time limit = time_limit * multiplier (prevents blowups from bad arms)")
    ap.add_argument("--ucb-weights", default=None,
                    help="Path to pre-trained LinUCB weights .npz (from --train mode)")
    ap.add_argument("--train", action="store_true",
                    help="Training mode: run UCB on all instances and save weights to outdir/ucb_weights.npz")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", action="store_true", help="Print per-round UCB decisions")
    args = ap.parse_args()

    rng = np.random.RandomState(args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load manifest
    manifest_path = Path(args.manifest)
    inst_dir = manifest_path.parent
    with open(manifest_path) as f:
        manifest = json.load(f)
    rng.shuffle(manifest)
    manifest = manifest[:args.n]

    # Load features
    uc_feats = load_features_npz(args.uc_features_npz)
    lp_feats = load_features_npz(args.lp_features_npz) if args.lp_features_npz else {}

    # LP feature index for lp_time_alloff (used for easy-instance detection)
    lp_feat_names = []
    if args.lp_features_npz:
        _npz = np.load(args.lp_features_npz, allow_pickle=True)
        lp_feat_names = [str(x) for x in _npz["feature_names"].tolist()]
    lp_time_idx = lp_feat_names.index("lp_time_alloff") if "lp_time_alloff" in lp_feat_names else None

    def get_instance_feats(inst_name: str) -> Optional[np.ndarray]:
        parts = []
        if inst_name in uc_feats:
            parts.append(uc_feats[inst_name])
        if inst_name in lp_feats:
            parts.append(lp_feats[inst_name])
        return np.concatenate(parts).astype(np.float32) if parts else None

    def is_easy(alloff_solve_time: float) -> bool:
        """Return True if all_off full solve was fast (below easy_threshold)."""
        return alloff_solve_time < args.easy_threshold

    # Compute context dimension for LinUCB (needed to initialise or load weights)
    sample_inst = next(iter(uc_feats.values())) if uc_feats else None
    sample_lp = next(iter(lp_feats.values())) if lp_feats else None
    d_inst = (len(sample_inst) if sample_inst is not None else 0) + \
             (len(sample_lp) if sample_lp is not None else 0)
    d_ctx = 5 + d_inst  # 5 LP state features + instance features

    # Load or initialise shared LinUCB (persisted across instances in train mode)
    if args.ucb_weights and Path(args.ucb_weights).exists():
        shared_ucb = LinUCB.load(args.ucb_weights)
        print(f"Loaded UCB weights from {args.ucb_weights}")
    else:
        shared_ucb = LinUCB(n_arms=N_ARMS, d=d_ctx, alpha=args.alpha)

    # Output files
    csv_path = outdir / "results.csv"
    jsonl_path = outdir / "results.jsonl"
    fieldnames = [
        "instance_name", "case",
        "t_alloff", "t_allon", "t_ucb",
        "status_alloff", "status_allon", "status_ucb",
        "delta_vs_alloff", "delta_vs_allon",
        "n_ucb_rounds", "warm_started", "easy_fallback",
    ]

    rows = []
    with open(csv_path, "w", newline="") as fcsv:
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        writer.writeheader()

        for entry in manifest:
            lp_rel = entry["lp"]
            lp_path = str(inst_dir / lp_rel)
            inst_name = Path(lp_rel).stem
            case = entry.get("case", "")

            if not Path(lp_path).exists():
                print(f"[WARN] missing: {lp_path}, skipping")
                continue

            inst_feats = get_instance_feats(inst_name)

            # Warm start from offline model
            warm_rewards = None
            warm_started = False
            if args.model_pt and inst_feats is not None:
                try:
                    warm_rewards = warm_start_from_offline_model(args.model_pt, inst_feats)
                    warm_started = True
                except Exception as e:
                    print(f"  [WARN] warm start failed: {e}")

            print(f"\n[{inst_name}]")

            # 1. all_off baseline
            r_off = solve_fixed_config(lp_path, all_on=False, time_limit=args.time_limit)
            print(f"  all_off:  {r_off['solve_time_sec']:.2f}s  [{r_off['status']}]")

            easy = is_easy(r_off["solve_time_sec"])

            # 2. all_on
            r_on = solve_fixed_config(lp_path, all_on=True, time_limit=args.time_limit)
            print(f"  all_on:   {r_on['solve_time_sec']:.2f}s  [{r_on['status']}]")

            # 3. UCB — fall back to all_on for easy instances to avoid exploration overhead
            if easy:
                r_ucb = r_on.copy()
                r_ucb["ucb_round_log"] = []
                r_ucb["n_ucb_rounds"] = 0
                print(f"  ucb:      {r_ucb['solve_time_sec']:.2f}s  [fallback=all_on, easy instance]")
            else:
                r_ucb = solve_with_ucb(
                    lp_path=lp_path,
                    instance_feats=inst_feats,
                    warm_start_rewards=warm_rewards,
                    time_limit=args.time_limit,
                    alpha=args.alpha,
                    max_rounds=args.max_rounds,
                    log=args.log,
                    time_limit_multiplier=args.ucb_time_multiplier,
                    shared_ucb=shared_ucb,
                )
                print(f"  ucb:      {r_ucb['solve_time_sec']:.2f}s  [{r_ucb['status']}]  "
                      f"rounds={r_ucb['n_ucb_rounds']}  warm={warm_started}")

            t_off = r_off["solve_time_sec"]
            t_on = r_on["solve_time_sec"]
            t_ucb = r_ucb["solve_time_sec"]

            denom_off = max(t_off, 1e-6)
            denom_on = max(t_on, 1e-6)
            delta_vs_alloff = (t_off - t_ucb) / denom_off
            delta_vs_allon = (t_on - t_ucb) / denom_on

            print(f"  delta vs all_off: {delta_vs_alloff:+.4f}  "
                  f"delta vs all_on: {delta_vs_allon:+.4f}")

            row = {
                "instance_name": inst_name,
                "case": case,
                "t_alloff": round(t_off, 4),
                "t_allon": round(t_on, 4),
                "t_ucb": round(t_ucb, 4),
                "status_alloff": r_off["status"],
                "status_allon": r_on["status"],
                "status_ucb": r_ucb["status"],
                "delta_vs_alloff": round(delta_vs_alloff, 6),
                "delta_vs_allon": round(delta_vs_allon, 6),
                "n_ucb_rounds": r_ucb["n_ucb_rounds"],
                "warm_started": warm_started,
                "easy_fallback": easy,
            }
            rows.append(row)
            writer.writerow(row)
            fcsv.flush()

            # write full record to jsonl (includes ucb_round_log)
            with open(jsonl_path, "a") as fjsonl:
                fjsonl.write(json.dumps({
                    **row,
                    "ucb_round_log": r_ucb["ucb_round_log"],
                    "warm_start_rewards": warm_rewards,
                }) + "\n")

    # Summary
    if rows:
        deltas_off = [r["delta_vs_alloff"] for r in rows]
        deltas_on = [r["delta_vs_allon"] for r in rows]
        summary = {
            "n": len(rows),
            "alpha": args.alpha,
            "easy_threshold": args.easy_threshold,
            "max_rounds": args.max_rounds,
            "n_easy_fallback": sum(r["easy_fallback"] for r in rows),
            "warm_started": sum(r["warm_started"] for r in rows),
            "mean_delta_vs_alloff": float(np.mean(deltas_off)),
            "median_delta_vs_alloff": float(np.median(deltas_off)),
            "pct_positive_vs_alloff": float(np.mean([d > 0 for d in deltas_off])),
            "mean_delta_vs_allon": float(np.mean(deltas_on)),
            "median_delta_vs_allon": float(np.median(deltas_on)),
            "pct_positive_vs_allon": float(np.mean([d > 0 for d in deltas_on])),
        }
        with open(outdir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        print("\n=== Summary ===")
        print(json.dumps(summary, indent=2))
    else:
        print("No results collected.")

    # Save UCB weights after training run
    if args.train:
        weights_path = str(outdir / "ucb_weights.npz")
        shared_ucb.save(weights_path)
        print(f"\nSaved UCB weights to {weights_path}")


if __name__ == "__main__":
    main()
