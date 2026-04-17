#!/usr/bin/env python3
"""
uc_branch.py

UC-aware branching rule for SCIP.

Unit Commitment MIPs have three types of binary variables:
  u[g,t]  — commitment (on/off):   binary, objective coefficient = 0
  v[g,t]  — startup:               binary, objective coefficient > 0  (startup cost)
  w[g,t]  — shutdown:              binary, objective coefficient > 0  (shutdown cost)

Commitment variables (u) drive feasibility of all second-stage constraints
(dispatch, reserve, ramping). Branching on them first gives tighter relaxations
at each node because fixing a commitment decision resolves all the dependent
continuous variable bounds.

Strategy:
  1. Among fractional LP candidates, prefer u[g,t] (binary, obj=0) variables.
  2. Among u candidates, branch on the most fractional one (LP value closest to 0.5).
  3. Fall back to SCIP's default (relpscost/full-strong) if no fractional u found.

Usage:
    from uc_branch import UCBranchrule, make_model_with_uc_branch
    m = make_model_with_uc_branch("instance.lp", time_limit=300)
    m.optimize()
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pyscipopt import Model, Branchrule, SCIP_RESULT


class UCBranchrule(Branchrule):
    """
    UC-aware branching rule.

    Identifies commitment variables (u[g,t]) at the start of B&B and
    prioritises them in fractional branching decisions.
    """

    def __init__(self, log: bool = False):
        self.log = log
        # Set at branchinitsol
        self._u_var_names: set = set()   # names of u[g,t] variables
        self._n_branches: int = 0
        self._n_uc_branches: int = 0

    def branchinitsol(self) -> None:
        """Called at start of B&B. Classify binary vars by objective coefficient."""
        model = self.model
        self._u_var_names = set()
        self._n_branches = 0
        self._n_uc_branches = 0

        try:
            for var in model.getVars():
                if var.vtype() == "BINARY" and abs(var.getObj()) < 1e-9:
                    self._u_var_names.add(var.name)
            if self.log:
                print(f"[UCBranch] identified {len(self._u_var_names)} commitment (u) vars")
        except Exception as e:
            if self.log:
                print(f"[UCBranch] classification failed: {e}")

    def branchexeclp(self, allowaddcons: bool) -> Dict[str, Any]:
        """Branch on most-fractional commitment variable, else fall back."""
        model = self.model
        self._n_branches += 1

        try:
            cands, sol_vals, fracs, n_cands, n_prio, n_frac_impl = model.getLPBranchCands()
        except Exception:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        if not cands:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        # Filter to fractional u[g,t] candidates
        u_cands: List[Tuple[float, Any]] = []
        for var, frac in zip(cands, fracs):
            if var.name in self._u_var_names and frac > 1e-6:
                # fractionality = distance to nearest integer, max at 0.5
                u_cands.append((frac, var))

        if not u_cands:
            # No fractional commitment vars — let SCIP decide
            return {"result": SCIP_RESULT.DIDNOTRUN}

        # Branch on the most fractional u var (closest to 0.5)
        # frac is already the fractional part; |frac - 0.5| is distance from 0.5
        best_frac, best_var = min(u_cands, key=lambda x: abs(x[0] - 0.5))

        try:
            model.branchVar(best_var)
            self._n_uc_branches += 1
            if self.log and self._n_branches % 100 == 0:
                pct = 100 * self._n_uc_branches / self._n_branches
                print(f"[UCBranch] branch #{self._n_branches}: "
                      f"chose {best_var.name} (frac={best_frac:.3f}), "
                      f"UC branch rate={pct:.1f}%")
            return {"result": SCIP_RESULT.BRANCHED}
        except Exception as e:
            if self.log:
                print(f"[UCBranch] branchVar failed: {e}")
            return {"result": SCIP_RESULT.DIDNOTRUN}

    def branchexitsol(self) -> None:
        if self.log and self._n_branches > 0:
            pct = 100 * self._n_uc_branches / self._n_branches
            print(f"[UCBranch] total branches={self._n_branches}, "
                  f"UC-guided={self._n_uc_branches} ({pct:.1f}%)")

    def get_stats(self) -> Dict[str, int]:
        return {
            "n_branches": self._n_branches,
            "n_uc_branches": self._n_uc_branches,
        }


def make_model_with_uc_branch(
    lp_path: str,
    time_limit: int = 300,
    log: bool = False,
    hide_output: bool = True,
) -> Tuple[Model, UCBranchrule]:
    """
    Create a SCIP Model with the UC-aware branching rule registered.

    The branching rule runs at priority 100000 — higher than SCIP's default
    relpscost (10000) so it gets first pick on each fractional LP solution.

    Returns (model, branch_rule).
    """
    m = Model()
    if hide_output:
        m.hideOutput(True)
    m.setRealParam("limits/time", float(time_limit))

    branch_rule = UCBranchrule(log=log)
    m.includeBranchrule(
        branch_rule,
        name="uc_commit_first",
        desc="Branch on UC commitment vars (u[g,t]) before startup/shutdown vars",
        priority=100_000,
        maxdepth=-1,
        maxbounddist=1.0,
    )

    m.readProblem(lp_path)
    return m, branch_rule
