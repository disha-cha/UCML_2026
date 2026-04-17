#!/usr/bin/env python3
"""
collect_cut_data.py

Collect per-cut training data for ML-based cut quality prediction.

For each instance, runs SCIP to the root node only, intercepts all generated
cuts, and records:
  - Per-cut features (8 scalar quality metrics)
  - Per-cut lookahead label: LP objective improvement from adding that cut

The lookahead label is the oracle: it tells us which cuts actually improved
the LP bound, not just which ones SCIP's heuristics rated highly.

Output .npz per instance (or combined), with:
  features   : float32 (N_cuts, N_features)
  labels     : float32 (N_cuts,)  — lookahead LP improvement, normalized
  feat_names : object  (N_features,)
  instance   : str

Usage:
  python src/collect_cut_data.py \\
    --manifest data/instances_v3/manifest_train.json \\
    --outfile experiments/step7_cut_data/cut_training_data.npz \\
    --max-rounds 5 \\
    --time-limit 60

Then train the cut quality model:
  python src/train_cut_model.py \\
    --data experiments/step7_cut_data/cut_training_data.npz \\
    --outdir experiments/step7_cut_data/
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from pyscipopt import Model, Sepa, SCIP_RESULT

from cut_quality_sepa import CUT_FEATURE_NAMES, N_CUT_FEATURES, _extract_cut_features


class CutDataCollector(Sepa):
    """
    Separator that records per-cut features and lookahead labels.

    Runs at priority -1 (after all standard separators), so the separation
    storage is full when this runs.
    """

    def __init__(self, max_rounds: int = 5, log: bool = False):
        self.max_rounds = max_rounds
        self.log = log
        self._round = 0
        self.data: List[Dict[str, Any]] = []   # one entry per separation round

    def sepaexeclp(self) -> Dict[str, Any]:
        model = self.model

        # Root node only
        try:
            if model.getDepth() > 0:
                return {"result": SCIP_RESULT.DIDNOTRUN}
        except Exception:
            pass

        if self._round >= self.max_rounds:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        try:
            cuts = model.getCuts()
        except Exception:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        if not cuts:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        # Extract features for each cut
        feats = np.stack([_extract_cut_features(c, model) for c in cuts], axis=0)

        # Lookahead labels: LP improvement from adding each cut
        labels = np.zeros(len(cuts), dtype=np.float32)
        try:
            lp_obj_before = float(model.getLPObjVal())
        except Exception:
            lp_obj_before = 0.0

        for i, cut in enumerate(cuts):
            try:
                lp_obj_after = float(model.getCutLookaheadLPObjval(cut))
                if np.isfinite(lp_obj_after):
                    # Normalize improvement by |current LP obj|
                    denom = max(abs(lp_obj_before), 1e-6)
                    labels[i] = float((lp_obj_after - lp_obj_before) / denom)
                else:
                    labels[i] = 0.0
            except Exception:
                labels[i] = 0.0

        # Clip label range to prevent outliers
        labels = np.clip(labels, -1.0, 1.0)

        self.data.append({
            "round": self._round,
            "n_cuts": len(cuts),
            "features": feats,
            "labels": labels,
            "lp_obj_before": lp_obj_before,
        })

        if self.log:
            good = (labels > 0).sum()
            print(f"  [collect round {self._round}] "
                  f"{len(cuts)} cuts, {good} with positive lookahead, "
                  f"max_label={labels.max():.4f}")

        self._round += 1
        return {"result": SCIP_RESULT.DIDNOTRUN}

    def get_arrays(self):
        """Return (features, labels) stacked across all rounds."""
        if not self.data:
            return np.zeros((0, N_CUT_FEATURES), dtype=np.float32), np.zeros(0, dtype=np.float32)
        X = np.concatenate([d["features"] for d in self.data], axis=0)
        y = np.concatenate([d["labels"] for d in self.data], axis=0)
        return X, y


def collect_instance(lp_path: str, max_rounds: int, time_limit: float, log: bool) -> Optional[Dict]:
    """Run root-only solve and collect cut data. Returns dict or None on failure."""
    m = Model()
    m.hideOutput(True)
    m.setRealParam("limits/time", time_limit)
    m.setLongintParam("limits/nodes", 1)
    m.setIntParam("separating/maxroundsroot", max_rounds + 2)  # allow a few extra
    m.setIntParam("separating/maxrounds", 0)

    collector = CutDataCollector(max_rounds=max_rounds, log=log)
    m.includeSepa(
        collector,
        name="cut_data_collector",
        desc="Record per-cut features and lookahead labels",
        priority=-1,
        freq=1,
    )

    m.readProblem(lp_path)
    try:
        m.optimize()
    except Exception as e:
        return None

    X, y = collector.get_arrays()
    if len(X) == 0:
        return None

    return {"features": X, "labels": y}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--outfile", required=True)
    ap.add_argument("--max-rounds", type=int, default=5,
                    help="Max separation rounds to record per instance")
    ap.add_argument("--time-limit", type=float, default=60.0,
                    help="Per-instance time limit (root solve only, should be short)")
    ap.add_argument("--max-instances", type=int, default=None)
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    inst_dir = manifest_path.parent
    with open(manifest_path) as f:
        manifest = json.load(f)
    if args.max_instances:
        manifest = manifest[:args.max_instances]

    Path(args.outfile).parent.mkdir(parents=True, exist_ok=True)

    all_X: List[np.ndarray] = []
    all_y: List[np.ndarray] = []
    instance_names: List[str] = []
    n_success = 0

    for entry in manifest:
        lp_rel = entry["lp"]
        lp_path = str(inst_dir / lp_rel)
        inst_name = Path(lp_rel).stem

        if not Path(lp_path).exists():
            print(f"[WARN] missing: {lp_path}, skipping")
            continue

        print(f"[{inst_name}] collecting...", end=" ", flush=True)
        t0 = time.time()
        result = collect_instance(lp_path, args.max_rounds, args.time_limit, args.log)
        elapsed = time.time() - t0

        if result is None:
            print(f"no cuts collected ({elapsed:.1f}s)")
            continue

        X, y = result["features"], result["labels"]
        all_X.append(X)
        all_y.append(y)
        # one name per cut row (not per instance) — store instance name as prefix
        instance_names.extend([inst_name] * len(X))
        n_success += 1
        good = (y > 0).sum()
        print(f"{len(X)} cuts, {good} positive lookahead  ({elapsed:.1f}s)")

    if not all_X:
        raise SystemExit("No cut data collected.")

    X_all = np.concatenate(all_X, axis=0).astype(np.float32)
    y_all = np.concatenate(all_y, axis=0).astype(np.float32)

    np.savez(
        args.outfile,
        features=X_all,
        labels=y_all,
        feature_names=np.array(CUT_FEATURE_NAMES, dtype=object),
        instance_names=np.array(instance_names, dtype=object),
    )

    print(f"\nSaved {X_all.shape} feature matrix and {y_all.shape} labels to {args.outfile}")
    print(f"  {n_success}/{len(manifest)} instances contributed data")
    print(f"  Label stats: mean={y_all.mean():.4f}  "
          f"pct_positive={(y_all > 0).mean():.1%}")


if __name__ == "__main__":
    main()
