#!/usr/bin/env python3
"""
ucb_sepa.py

Linear UCB meta-separator for adaptive cut selection during SCIP solving.

Architecture:
  - Registered as a high-priority separator so it runs FIRST each round
  - At each separation round, observes LP state and uses LinUCB to decide
    which separators to enable for that round
  - Measures reward = normalized LP dual bound improvement from last round
  - Updates LinUCB estimates after each round
  - Optionally warm-started from an offline-trained MLP classifier

Arms: the 8 standard SCIP separators (one arm = one separator on/off)
Context: LP state features at the start of each round + static instance features

Usage (standalone):
  from ucb_sepa import UCBSepa, make_model_with_ucb
  model = make_model_with_ucb("instance.lp", time_limit=300)
  model.optimize()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from pyscipopt import Model, Sepa, SCIP_RESULT

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------

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
N_ARMS = len(SEPAS)

# UCB priority: high positive = runs before constraint handlers / other separators
UCB_SEPA_PRIORITY = 10_000


# -----------------------------------------------------------------------
# Linear UCB (one model per arm, disjoint)
# -----------------------------------------------------------------------

class LinUCB:
    """
    Disjoint Linear UCB bandit.

    For each arm a:
        A_a  (d x d) initialized to I
        b_a  (d,)    initialized to 0
        theta_a = A_a^{-1} b_a

    UCB score for arm a given context x:
        score_a = theta_a @ x + alpha * sqrt(x @ A_a^{-1} @ x)
    """

    def __init__(self, n_arms: int, d: int, alpha: float = 1.0):
        self.n_arms = n_arms
        self.d = d
        self.alpha = alpha
        self.A = [np.eye(d, dtype=np.float64) for _ in range(n_arms)]
        self.b = [np.zeros(d, dtype=np.float64) for _ in range(n_arms)]

    def score(self, arm: int, x: np.ndarray) -> float:
        A_inv = np.linalg.inv(self.A[arm])
        theta = A_inv @ self.b[arm]
        return float(theta @ x + self.alpha * np.sqrt(x @ A_inv @ x))

    def scores(self, x: np.ndarray) -> np.ndarray:
        return np.array([self.score(a, x) for a in range(self.n_arms)])

    def update(self, arm: int, x: np.ndarray, reward: float) -> None:
        self.A[arm] += np.outer(x, x)
        self.b[arm] += reward * x

    def warm_start_arm(self, arm: int, x: np.ndarray, reward: float, n_pseudo: int = 10) -> None:
        """Add n_pseudo synthetic observations for arm with given reward."""
        for _ in range(n_pseudo):
            self.update(arm, x, reward)

    def save(self, path: str) -> None:
        """Save A and b matrices to .npz for cross-instance persistence."""
        np.savez(
            path,
            A=np.stack(self.A, axis=0),
            b=np.stack(self.b, axis=0),
            n_arms=np.array(self.n_arms),
            d=np.array(self.d),
            alpha=np.array(self.alpha),
        )

    @classmethod
    def load(cls, path: str) -> "LinUCB":
        """Load previously saved LinUCB weights."""
        data = np.load(path)
        obj = cls(
            n_arms=int(data["n_arms"]),
            d=int(data["d"]),
            alpha=float(data["alpha"]),
        )
        obj.A = [data["A"][i] for i in range(obj.n_arms)]
        obj.b = [data["b"][i] for i in range(obj.n_arms)]
        return obj


# -----------------------------------------------------------------------
# LP state feature extraction (called inside sepaexeclp)
# -----------------------------------------------------------------------

def get_lp_context(model: Model, root_lp_obj: float, max_rounds: int = 10) -> np.ndarray:
    """
    Extract a context vector from current LP state.
    Returns a fixed-length float32 array.

    Features:
      0: lp_obj_improvement  -- (current - root) / |root|, capped [-1, 1]
      1: round_frac          -- current round / max_rounds
      2: n_rows_frac         -- (current rows - initial rows) / initial rows
      3: lp_iters_log        -- log(n_lp_iterations + 1) / log(100001)
      4: at_root             -- 1 if depth == 0 else 0
    """
    try:
        lp_obj = float(model.getLPObjVal())
    except Exception:
        lp_obj = root_lp_obj

    try:
        n_rounds = int(model.getNSepaRounds())
    except Exception:
        n_rounds = 0

    try:
        n_rows = int(model.getNLPRows())
    except Exception:
        n_rows = 0

    try:
        n_iters = int(model.getNLPIterations())
    except Exception:
        n_iters = 0

    try:
        depth = int(model.getDepth())
    except Exception:
        depth = 0

    denom = max(abs(root_lp_obj), 1e-6)
    lp_improvement = float(np.clip((lp_obj - root_lp_obj) / denom, -1.0, 1.0))
    round_frac = float(np.clip(n_rounds / max(max_rounds, 1), 0.0, 1.0))
    rows_frac = float(np.clip(n_rows / max(n_rows, 1), 0.0, 1.0))
    iters_log = float(np.log1p(n_iters) / np.log1p(100_000))
    at_root = float(depth == 0)

    return np.array([lp_improvement, round_frac, rows_frac, iters_log, at_root], dtype=np.float64)


# -----------------------------------------------------------------------
# UCB Separator
# -----------------------------------------------------------------------

class UCBSepa(Sepa):
    """
    Meta-separator that uses Linear UCB to adaptively select which
    SCIP separators to enable each round.

    Parameters
    ----------
    instance_feats : np.ndarray or None
        Static instance features (from uc_features + lp_features npz).
        If None, only LP state features are used as context.
    alpha : float
        UCB exploration parameter.
    max_rounds : int
        Expected max separation rounds (for feature normalization).
    warm_start_rewards : dict or None
        {sepa_name: reward_value} — initial pseudo-observations per arm.
        Typically derived from offline model predictions.
    log : bool
        If True, print per-round decisions to stdout.
    """

    def __init__(
        self,
        instance_feats: Optional[np.ndarray] = None,
        alpha: float = 1.0,
        max_rounds: int = 10,
        warm_start_rewards: Optional[Dict[str, float]] = None,
        log: bool = False,
        shared_ucb: Optional["LinUCB"] = None,
    ):
        self.instance_feats = instance_feats  # static, shape (d_inst,)
        self.alpha = alpha
        self.max_rounds = max_rounds
        self.log = log

        # context dimension: LP features + instance features
        d_lp = 5  # from get_lp_context
        d_inst = len(instance_feats) if instance_feats is not None else 0
        self.d = d_lp + d_inst

        # Use shared (cross-instance) UCB if provided, otherwise create fresh one
        self.ucb = shared_ucb if shared_ucb is not None else LinUCB(n_arms=N_ARMS, d=self.d, alpha=alpha)
        self._owns_ucb = shared_ucb is None  # only warm-start if we own the UCB

        # tracking
        self.prev_lp_obj: Optional[float] = None
        self.root_lp_obj: Optional[float] = None
        self.prev_action: Optional[int] = None
        self.prev_context: Optional[np.ndarray] = None
        self.round_log: List[Dict[str, Any]] = []

        # apply warm start only when we own the UCB (not cross-instance mode)
        if warm_start_rewards and self._owns_ucb:
            self._apply_warm_start(warm_start_rewards)

    def _apply_warm_start(self, rewards: Dict[str, float]) -> None:
        """Add pseudo-observations from offline model predictions."""
        # build a neutral context (all zeros = "before any rounds")
        x0 = np.zeros(self.d, dtype=np.float64)
        if self.instance_feats is not None:
            # normalize instance feats roughly
            inst = self.instance_feats.astype(np.float64)
            norm = np.linalg.norm(inst)
            if norm > 1e-8:
                inst = inst / norm
            x0[5:] = inst

        for i, sepa in enumerate(SEPAS):
            if sepa in rewards:
                self.ucb.warm_start_arm(i, x0, float(rewards[sepa]), n_pseudo=10)

    def _build_context(self) -> np.ndarray:
        """Concatenate LP state + instance features into context vector."""
        lp_ctx = get_lp_context(
            self.model,
            root_lp_obj=self.root_lp_obj or 0.0,
            max_rounds=self.max_rounds,
        )
        if self.instance_feats is not None:
            inst = self.instance_feats.astype(np.float64)
            norm = np.linalg.norm(inst)
            if norm > 1e-8:
                inst = inst / norm
            return np.concatenate([lp_ctx, inst])
        return lp_ctx

    def _enable_only(self, arm: int) -> None:
        """Enable only the chosen separator; disable all others."""
        for i, sepa in enumerate(SEPAS):
            freq = 1 if i == arm else 0
            try:
                self.model.setIntParam(f"separating/{sepa}/freq", freq)
            except Exception:
                pass

    def _enable_all(self) -> None:
        for sepa in SEPAS:
            try:
                self.model.setIntParam(f"separating/{sepa}/freq", 1)
            except Exception:
                pass

    def sepainitsol(self) -> None:
        """Called at the start of B&B. Record root LP objective and row count."""
        try:
            self.root_lp_obj = float(self.model.getLPObjVal())
        except Exception:
            self.root_lp_obj = None
        try:
            self.prev_n_rows = int(self.model.getNLPRows())
        except Exception:
            self.prev_n_rows = 0
        self.prev_lp_obj = self.root_lp_obj
        self.prev_action = None
        self.prev_context = None
        self.round_log = []

    def sepaexeclp(self) -> Dict[str, Any]:
        """Called at the start of each separation round."""
        model = self.model

        # Only run UCB at root node — deeper nodes use whatever freq was last set
        try:
            if model.getDepth() > 0:
                return {"result": SCIP_RESULT.DIDNOTRUN}
        except Exception:
            pass

        # initialize root obj on first call if sepainitsol didn't catch it
        if self.root_lp_obj is None:
            try:
                self.root_lp_obj = float(model.getLPObjVal())
            except Exception:
                self.root_lp_obj = 0.0
            self.prev_lp_obj = self.root_lp_obj
            try:
                self.prev_n_rows = int(model.getNLPRows())
            except Exception:
                self.prev_n_rows = 0

        # --- Update UCB from previous round's reward (node-count proxy) ---
        if self.prev_action is not None and self.prev_context is not None:
            try:
                cur_lp_obj = float(model.getLPObjVal())
            except Exception:
                cur_lp_obj = self.prev_lp_obj
            try:
                cur_n_rows = int(model.getNLPRows())
            except Exception:
                cur_n_rows = self.prev_n_rows

            bound_improvement = cur_lp_obj - self.prev_lp_obj
            rows_added = max(cur_n_rows - self.prev_n_rows, 1)
            bound_denom = max(abs(self.root_lp_obj), 1e-6)

            # Reward = bound improvement per row added, normalized by root obj.
            # High-quality cuts close more gap per row — predict fewer B&B nodes.
            reward = float((bound_improvement / rows_added) / bound_denom)

            self.ucb.update(self.prev_action, self.prev_context, reward)
            self.prev_lp_obj = cur_lp_obj
            self.prev_n_rows = cur_n_rows

        # --- Choose arm for this round ---
        context = self._build_context()
        scores = self.ucb.scores(context)
        arm = int(np.argmax(scores))

        # Enable only chosen separator
        self._enable_only(arm)

        if self.log:
            round_n = len(self.round_log)
            print(f"  [UCB round {round_n}] chose={SEPAS[arm]}  "
                  f"scores={np.round(scores, 3).tolist()}")

        self.round_log.append({
            "round": len(self.round_log),
            "arm": arm,
            "sepa": SEPAS[arm],
            "scores": scores.tolist(),
        })

        self.prev_action = arm
        self.prev_context = context

        # We're a meta-separator — we don't add cuts ourselves
        return {"result": SCIP_RESULT.DIDNOTRUN}

    def sepaexitsol(self) -> None:
        """Re-enable all separators on exit (clean state for next solve)."""
        self._enable_all()

    def get_log(self) -> List[Dict[str, Any]]:
        return self.round_log


# -----------------------------------------------------------------------
# Factory: build a SCIP model with UCB separator included
# -----------------------------------------------------------------------

def make_model_with_ucb(
    lp_path: str,
    time_limit: int = 300,
    alpha: float = 1.0,
    max_rounds: int = 10,
    instance_feats: Optional[np.ndarray] = None,
    warm_start_rewards: Optional[Dict[str, float]] = None,
    log: bool = False,
    hide_output: bool = True,
    time_limit_multiplier: float = 2.0,
    shared_ucb: Optional["LinUCB"] = None,
) -> Tuple[Model, UCBSepa]:
    """
    Create a SCIP Model with the UCB meta-separator registered.

    Returns (model, ucb_sepa) — call model.optimize() to solve.

    time_limit_multiplier: UCB solve is capped at time_limit * multiplier to
        prevent runaway solves from bad arm choices.
    """
    m = Model()
    if hide_output:
        m.hideOutput(True)

    # Cap UCB solve time to avoid catastrophic blowups from bad arm choices
    ucb_time_limit = float(time_limit) * time_limit_multiplier
    m.setRealParam("limits/time", ucb_time_limit)
    m.setIntParam("separating/maxroundsroot", max_rounds)
    m.setIntParam("separating/maxrounds", max_rounds)

    # Start with all separators off — UCB will selectively enable them each round
    for sepa in SEPAS:
        try:
            m.setIntParam(f"separating/{sepa}/freq", 0)
        except Exception:
            pass

    sepa_plugin = UCBSepa(
        instance_feats=instance_feats,
        alpha=alpha,
        max_rounds=max_rounds,
        warm_start_rewards=warm_start_rewards,
        log=log,
        shared_ucb=shared_ucb,
    )

    # High priority so UCB runs before all other separators each round
    m.includeSepa(
        sepa_plugin,
        name="ucb_meta",
        desc="Linear UCB adaptive separator selection",
        priority=UCB_SEPA_PRIORITY,
        freq=1,
    )

    m.readProblem(lp_path)
    return m, sepa_plugin


# -----------------------------------------------------------------------
# Warm-start helper: derive rewards from offline model predictions
# -----------------------------------------------------------------------

def warm_start_from_offline_model(
    model_pt_path: str,
    instance_feats: np.ndarray,
) -> Dict[str, float]:
    """
    Load the offline MLP and convert its softmax output into per-separator
    initial reward estimates.

    The offline model predicts over configs (e.g. "strongcg_only", "all_on").
    We map each predicted class to individual separator reward boosts:
      - "all_on"    -> small positive boost for all separators
      - "<sepa>_only" -> larger boost for that specific separator
      - "all_off"   -> no boost (neutral)

    Returns dict {sepa_name: reward_float}.
    """
    import torch

    # Inline MLP definition (must match train_uc_k1_offline.py)
    import torch.nn as nn

    class MLP(nn.Module):
        def __init__(self, d_in, n_classes, hidden=128, depth=2, dropout=0.1):
            super().__init__()
            layers = []
            d = d_in
            for _ in range(depth):
                layers += [nn.Linear(d, hidden), nn.ReLU(), nn.Dropout(dropout)]
                d = hidden
            layers.append(nn.Linear(d, n_classes))
            self.net = nn.Sequential(*layers)

        def forward(self, x):
            return self.net(x)

    ckpt = torch.load(model_pt_path, map_location="cpu")
    classes = ckpt["classes"]
    model = MLP(ckpt["d_in"], len(classes), ckpt["hidden"], ckpt["depth"], ckpt["dropout"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    x = torch.tensor(instance_feats, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1).squeeze().numpy()

    # Map config probabilities to per-separator reward boosts
    rewards: Dict[str, float] = {s: 0.0 for s in SEPAS}
    for cls, prob in zip(classes, probs):
        if cls == "all_off":
            pass  # no boost
        elif cls == "all_on":
            for s in SEPAS:
                rewards[s] += float(prob) * 0.1
        elif cls.endswith("_only"):
            sepa = cls.replace("_only", "")
            if sepa in rewards:
                rewards[sepa] += float(prob) * 0.5
        else:
            # named combos like "binary_structure", "gomory_family" etc.
            # boost component separators proportionally
            _COMBO_MAP = {
                "binary_structure":  ["clique", "zerohalf"],
                "temporal_coupling": ["cmir", "impliedbounds"],
                "strong_cuts":       ["gomory", "strongcg"],
                "flow_based":        ["flowcover", "aggregation"],
                "mix_balanced":      ["clique", "flowcover", "impliedbounds", "aggregation"],
                "mix_aggressive":    ["gomory", "cmir", "strongcg", "zerohalf"],
                "mix_uc_motivated":  ["cmir", "clique", "impliedbounds", "zerohalf"],
                "gomory_family":     ["gomory", "strongcg", "cmir", "aggregation"],
                "no_gomory":         ["cmir", "clique", "flowcover", "zerohalf",
                                      "strongcg", "aggregation", "impliedbounds"],
                "no_clique":         ["gomory", "cmir", "flowcover", "zerohalf",
                                      "strongcg", "aggregation", "impliedbounds"],
            }
            members = _COMBO_MAP.get(cls, [])
            for s in members:
                if s in rewards:
                    rewards[s] += float(prob) * 0.3 / max(len(members), 1)

    return rewards
