#!/usr/bin/env python3
"""
extract_lp_features.py

Extract LP-based features from UC instances by running SCIP at the root node only
(no branch-and-bound). Two quick solves per instance:

  1. all_off  (pure LP relaxation, no cuts)
  2. all_on   (LP + cutting plane rounds at root)

Captures:
  - n_vars, n_binvars, n_conss: problem dimensions
  - root_lp_obj:       dual bound after pure LP relaxation (all_off)
  - root_cuts_obj:     dual bound after cut rounds at root (all_on)
  - cut_tightening:    (root_cuts_obj - root_lp_obj) / max(|root_lp_obj|, 1e-6)
                       key predictor: large value -> cuts help a lot
  - lp_iters_alloff:   LP iterations for pure LP solve
  - lp_iters_allon:    LP iterations including cut rounds
  - n_cuts_added:      LP rows added by cutting planes (allon rows - alloff rows)
  - lp_time_alloff:    wall time for pure LP root solve
  - lp_time_allon:     wall time for LP + cuts root solve

Output: .npz with keys features, feature_names, instance_names
  (same format as uc_features.npz, ready to concatenate)

Usage:
  python src/extract_lp_features.py \
    --manifest data/instances_v2/manifest.json \
    --outfile experiments/step2_features_v2/lp_features.npz
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from pyscipopt import Model

SEPAS = [
    "gomory", "cmir", "clique", "flowcover",
    "zerohalf", "strongcg", "aggregation", "impliedbounds",
]

FEATURE_NAMES = [
    "n_vars",
    "n_binvars",
    "n_conss",
    "root_lp_obj",
    "root_cuts_obj",
    "cut_tightening",
    "lp_iters_alloff",
    "lp_iters_allon",
    "n_cuts_added",
    "lp_time_alloff",
    "lp_time_allon",
]


def _root_solve(lp_path: str, all_on: bool, time_limit: float = 120.0) -> Dict[str, Any]:
    """Run SCIP to root node only, return LP stats."""
    m = Model()
    m.hideOutput(True)
    m.setRealParam("limits/time", time_limit)
    m.setLongintParam("limits/nodes", 1)
    m.setIntParam("separating/maxroundsroot", 10 if all_on else 0)
    m.setIntParam("separating/maxrounds", 0)

    for sepa in SEPAS:
        freq = 1 if all_on else 0
        try:
            m.setIntParam(f"separating/{sepa}/freq", freq)
        except Exception:
            pass

    m.readProblem(lp_path)

    n_vars = m.getNVars()
    n_binvars = sum(1 for v in m.getVars() if v.vtype() == "BINARY")
    n_conss = m.getNConss()

    t0 = time.time()
    m.optimize()
    wall = time.time() - t0

    try:
        dual = float(m.getDualbound())
    except Exception:
        dual = float("nan")

    try:
        lp_iters = int(m.getNLPIterations())
    except Exception:
        lp_iters = 0

    try:
        n_rows = m.getNRows()
    except Exception:
        n_rows = n_conss

    return {
        "n_vars": n_vars,
        "n_binvars": n_binvars,
        "n_conss": n_conss,
        "dual": dual,
        "lp_iters": lp_iters,
        "n_rows": n_rows,
        "wall": wall,
    }


def extract_lp_features(lp_path: str, time_limit: float = 120.0) -> np.ndarray:
    """Return feature vector of length len(FEATURE_NAMES)."""
    r_off = _root_solve(lp_path, all_on=False, time_limit=time_limit)
    r_on = _root_solve(lp_path, all_on=True, time_limit=time_limit)

    lp_obj = r_off["dual"]
    cuts_obj = r_on["dual"]
    denom = max(abs(lp_obj), 1e-6)
    cut_tightening = (cuts_obj - lp_obj) / denom

    n_cuts_added = max(0, r_on["n_rows"] - r_off["n_rows"])

    return np.array([
        r_off["n_vars"],
        r_off["n_binvars"],
        r_off["n_conss"],
        lp_obj,
        cuts_obj,
        cut_tightening,
        r_off["lp_iters"],
        r_on["lp_iters"],
        n_cuts_added,
        r_off["wall"],
        r_on["wall"],
    ], dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to manifest.json")
    ap.add_argument("--outfile", required=True, help="Output .npz path")
    ap.add_argument("--time-limit", type=float, default=120.0,
                    help="Per-solve time limit for root solves (sec)")
    ap.add_argument("--max-instances", type=int, default=None,
                    help="Cap for debugging")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    inst_dir = manifest_path.parent

    with open(manifest_path) as f:
        manifest = json.load(f)

    if args.max_instances:
        manifest = manifest[:args.max_instances]

    Path(args.outfile).parent.mkdir(parents=True, exist_ok=True)

    all_features: List[np.ndarray] = []
    instance_names: List[str] = []

    for entry in manifest:
        lp_rel = entry["lp"]
        lp_path = str(inst_dir / lp_rel)
        inst_name = Path(lp_rel).stem

        if not Path(lp_path).exists():
            print(f"[WARN] missing: {lp_path}, skipping")
            continue

        print(f"[LP] {inst_name} ...", end=" ", flush=True)
        try:
            feats = extract_lp_features(lp_path, time_limit=args.time_limit)
            all_features.append(feats)
            instance_names.append(inst_name)
            ct = feats[FEATURE_NAMES.index("cut_tightening")]
            n_cuts = int(feats[FEATURE_NAMES.index("n_cuts_added")])
            print(f"cut_tightening={ct:.4f}  n_cuts={n_cuts}")
        except Exception as e:
            print(f"FAILED: {e}")

    if not all_features:
        raise SystemExit("No features extracted.")

    X = np.stack(all_features, axis=0)
    np.savez(
        args.outfile,
        features=X,
        feature_names=np.array(FEATURE_NAMES, dtype=object),
        instance_names=np.array(instance_names, dtype=object),
    )
    print(f"\nSaved {X.shape} to {args.outfile}")
    print(f"Feature names: {FEATURE_NAMES}")


if __name__ == "__main__":
    main()
