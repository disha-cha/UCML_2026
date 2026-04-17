#!/usr/bin/env python3
"""
cut_quality_sepa.py

Cut quality filtering separator for SCIP.

After all standard separators have added their cuts to the separation storage,
this plugin scores every cut and keeps only the top-k using overrideCutSelection3.

Two modes:
  1. Heuristic (no model): composite score from SCIP built-in metrics
  2. ML (with trained model): predict cut quality from features

Heuristic composite score (equal-weight sum, all in [0,1] after clipping):
  - efficacy:          how violated is the cut? (higher = better)
  - obj_parallelism:   alignment with objective gradient (higher = better)
  - int_support:       fraction of nonzeros on integer vars (higher = better)
  - scip_score:        SCIP's native composite score (good baseline)

For ML mode:
  - Feature vector per cut: [violation, rel_violation, obj_parallelism,
                              efficacy, scip_score, exp_improv, support, int_support]
  - Label: LP objective improvement if cut added (from lookahead oracle during data collection)
  - Model: MLP regressor, trained offline from collected data

Usage (heuristic):
    from cut_quality_sepa import CutQualitySepa, make_model_with_cut_filter
    m, sepa = make_model_with_cut_filter("instance.lp", top_k=5)
    m.optimize()

Usage (ML):
    m, sepa = make_model_with_cut_filter("instance.lp", top_k=5, model_pt="cut_model.pt")
    m.optimize()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pyscipopt import Model, Sepa, SCIP_RESULT


# Names of features extracted per cut (must match collect_cut_data.py order)
CUT_FEATURE_NAMES = [
    "violation",
    "rel_violation",
    "obj_parallelism",
    "efficacy",
    "scip_score",
    "exp_improv",
    "support_score",
    "int_support",
]
N_CUT_FEATURES = len(CUT_FEATURE_NAMES)


def _extract_cut_features(cut, model: Model) -> np.ndarray:
    """Extract scalar quality features for a single cut. Returns float32 array."""
    feats = np.zeros(N_CUT_FEATURES, dtype=np.float32)
    score_funcs = [
        model.getCutViolation,
        model.getCutRelViolation,
        model.getCutObjParallelism,
        model.getCutEfficacy,
        model.getCutSCIPScore,
        model.getCutExpImprov,
        model.getCutSupportScore,
        model.getCutIntSupport,
    ]
    for i, fn in enumerate(score_funcs):
        try:
            v = fn(cut)
            feats[i] = float(v) if v is not None and np.isfinite(v) else 0.0
        except Exception:
            pass
    return feats


def _heuristic_score(feats: np.ndarray) -> float:
    """
    Composite heuristic score from cut feature vector.

    Weights chosen to balance:
    - Efficacy (main quality signal)
    - SCIP composite score (well-tuned baseline)
    - Objective parallelism (cuts aligned with obj move towards optimum)
    - Integer support (integer-support cuts tend to be tighter)
    """
    efficacy       = np.clip(feats[3], 0.0, 5.0) / 5.0
    obj_para       = np.clip(feats[2], 0.0, 1.0)
    int_support    = np.clip(feats[7], 0.0, 1.0)
    scip_score     = np.clip(feats[4], 0.0, 1.0)
    return float(0.4 * efficacy + 0.3 * scip_score + 0.2 * obj_para + 0.1 * int_support)


class CutQualitySepa(Sepa):
    """
    Cut quality filtering meta-separator.

    Runs at very low priority (after all standard separators have added cuts),
    scores each cut, and calls overrideCutSelection3 to keep only the top-k.

    Parameters
    ----------
    top_k : int
        Max number of cuts to keep per round. If there are fewer cuts, keeps all.
    min_efficacy : float
        Discard cuts with efficacy below this threshold (pre-filter).
    model_pt : str or None
        Path to trained MLP regressor for cut quality. If None, uses heuristic.
    log : bool
        Print per-round statistics.
    collect : bool
        If True, records cut features + scores for offline training data.
    """

    def __init__(
        self,
        top_k: int = 10,
        top_frac: Optional[float] = None,
        min_keep: int = 5,
        min_efficacy: float = 1e-4,
        model_pt: Optional[str] = None,
        log: bool = False,
        collect: bool = False,
    ):
        self.top_k = top_k
        # Fraction-based mode: keep top_frac of valid cuts, floored at min_keep.
        # When top_frac is set it replaces top_k and the filter_ratio gate —
        # the fraction naturally scales with pool size, so no fixed gate is needed.
        self.top_frac = top_frac
        self.min_keep = min_keep
        self.min_efficacy = min_efficacy
        self.log = log
        self.collect = collect

        # ML model (optional)
        self._ml_model = None
        self._mu: Optional[np.ndarray] = None
        self._sd: Optional[np.ndarray] = None
        if model_pt and Path(model_pt).exists():
            self._load_ml_model(model_pt)

        # Stats / data collection
        self.round_log: List[Dict[str, Any]] = []
        self._total_cuts_seen = 0
        self._total_cuts_kept = 0
        self._rounds_skipped = 0
        self._root_round = 0  # count of root separation rounds seen

    def _load_ml_model(self, model_pt: str) -> None:
        try:
            import torch
            import torch.nn as nn

            ckpt = torch.load(model_pt, map_location="cpu")
            d_in = ckpt.get("d_in", N_CUT_FEATURES)
            hidden = ckpt.get("hidden", 64)

            class MLP(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(d_in, hidden), nn.ReLU(),
                        nn.Linear(hidden, hidden), nn.ReLU(),
                        nn.Linear(hidden, 1),
                    )
                def forward(self, x):
                    return self.net(x).squeeze(-1)

            net = MLP()
            net.load_state_dict(ckpt["state_dict"])
            net.eval()
            self._ml_model = net
            self._mu = np.array(ckpt.get("mu", np.zeros(d_in)), dtype=np.float32)
            self._sd = np.array(ckpt.get("sd", np.ones(d_in)), dtype=np.float32)
            if self.log:
                print(f"[CutQuality] loaded ML model from {model_pt}")
        except Exception as e:
            if self.log:
                print(f"[CutQuality] ML model load failed ({e}), using heuristic")

    def _score_cuts(self, cuts: list, model: Model) -> np.ndarray:
        """Score all cuts. Returns float array of shape (n_cuts,)."""
        if not cuts:
            return np.array([], dtype=np.float32)

        feats = np.stack([_extract_cut_features(c, model) for c in cuts], axis=0)

        if self._ml_model is not None:
            try:
                import torch
                x = (feats - self._mu) / (self._sd + 1e-8)
                with torch.no_grad():
                    scores = self._ml_model(torch.tensor(x)).numpy().astype(np.float32)
                return scores
            except Exception:
                pass  # fallback to heuristic

        return np.array([_heuristic_score(feats[i]) for i in range(len(cuts))],
                        dtype=np.float32)

    def sepaexeclp(self) -> Dict[str, Any]:
        """Called each separation round. Score and filter cuts in sepastore."""
        model = self.model

        # Only filter at root node to avoid overhead in tree
        try:
            if model.getDepth() > 0:
                return {"result": SCIP_RESULT.DIDNOTRUN}
        except Exception:
            pass

        self._root_round += 1

        try:
            cuts = model.getCuts()
        except Exception:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        if not cuts:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        self._total_cuts_seen += len(cuts)

        # Pre-filter: discard cuts below min_efficacy
        try:
            valid_cuts = [c for c in cuts
                          if model.getCutEfficacy(c) >= self.min_efficacy]
        except Exception:
            valid_cuts = cuts

        if not valid_cuts:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        # Compute n_keep: fraction-based (if top_frac set) or fixed top_k
        if self.top_frac is not None:
            n_keep = max(self.min_keep, int(len(valid_cuts) * self.top_frac))
        else:
            n_keep = self.top_k

        # Skip if we'd keep everything anyway — no point calling overrideCutSelection
        if n_keep >= len(valid_cuts):
            self._rounds_skipped += 1
            if self.log:
                print(f"[CutQuality] round skipped (n_keep={n_keep} >= n_valid={len(valid_cuts)})")
            return {"result": SCIP_RESULT.DIDNOTRUN}

        scores = self._score_cuts(valid_cuts, model)
        n_keep = min(n_keep, len(valid_cuts))

        # Top-k by score
        top_idx = np.argpartition(scores, -n_keep)[-n_keep:]
        selected = [valid_cuts[i] for i in top_idx]

        self._total_cuts_kept += len(selected)

        # Record for data collection
        if self.collect:
            self.round_log.append({
                "depth": 0,
                "n_cuts_seen": len(cuts),
                "n_valid": len(valid_cuts),
                "n_kept": len(selected),
                "scores": scores.tolist(),
            })

        try:
            model.overrideCutSelection3(selected)
        except Exception as e:
            if self.log:
                print(f"[CutQuality] overrideCutSelection3 failed: {e}")
            return {"result": SCIP_RESULT.DIDNOTRUN}

        if self.log:
            print(f"[CutQuality] round: {len(cuts)} cuts → kept {len(selected)} "
                  f"(best score={scores[top_idx].max():.4f})")

        return {"result": SCIP_RESULT.DIDNOTRUN}  # we don't add cuts ourselves

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_cuts_seen": self._total_cuts_seen,
            "total_cuts_kept": self._total_cuts_kept,
            "keep_rate": (self._total_cuts_kept / max(self._total_cuts_seen, 1)),
            "n_rounds": len(self.round_log),
            "n_rounds_skipped": self._rounds_skipped,
        }

    def get_log(self) -> List[Dict[str, Any]]:
        return self.round_log


def make_model_with_cut_filter(
    lp_path: str,
    time_limit: int = 300,
    top_k: int = 10,
    top_frac: Optional[float] = None,
    min_keep: int = 5,
    min_efficacy: float = 1e-4,
    model_pt: Optional[str] = None,
    log: bool = False,
    collect: bool = False,
    hide_output: bool = True,
) -> Tuple[Model, CutQualitySepa]:
    """
    Create a SCIP Model with the cut quality filter separator registered.

    The filter runs at priority -1 (after all standard separators, which have
    priority ≥ 0) so it sees ALL cuts before SCIP applies them.

    Returns (model, cut_quality_sepa).
    """
    m = Model()
    if hide_output:
        m.hideOutput(True)
    m.setRealParam("limits/time", float(time_limit))

    sepa = CutQualitySepa(
        top_k=top_k,
        top_frac=top_frac,
        min_keep=min_keep,
        min_efficacy=min_efficacy,
        model_pt=model_pt,
        log=log,
        collect=collect,
    )
    m.includeSepa(
        sepa,
        name="cut_quality_filter",
        desc="Score and filter cuts by quality; keep top-k per round",
        priority=-1,       # run after all standard separators (priority ≥ 0)
        freq=1,
    )

    m.readProblem(lp_path)
    return m, sepa
