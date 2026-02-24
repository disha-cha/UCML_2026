#!/usr/bin/env python3
"""
eval_uc_k1_online_policy.py  (K1 classifier version)

Online evaluation for offline-trained k1 policy:
- Model is a classifier: f(UC_features) -> logits over classes
  (NOT the onehot-augmented reward model).
- Loads UC features from uc_features.npz
- Loads config vectors (sepa_freq dict) from results.jsonl
- Samples N instances from manifest.json
- Runs baseline config vs predicted config in SCIP
- Writes per-instance rows + summary metrics.

This fixes the shape mismatch you saw:
  mat1 (5x26) vs mat2 (21x128)
by feeding ONLY 21-dim UC features to the trained model.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import pyscipopt as pyopt


SEPA_KEYS_DEFAULT = [
    "gomory",
    "cmir",
    "clique",
    "flowcover",
    "zerohalf",
    "strongcg",
    "aggregation",
    "impliedbounds",
]


# -------------------------
# Model (must match train_uc_k1_offline.py classifier)
# -------------------------

class ClassifierMLP(nn.Module):
    def __init__(self, d_in: int, hidden: int, n_classes: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# -------------------------
# Helpers
# -------------------------

def _norm_inst_name(name: str) -> str:
    s = str(name)
    for suf in [".lp", ".mps", ".mps.gz", ".proto.lp", ".json", ".minud", ".minud.json"]:
        if s.endswith(suf):
            s = s[: -len(suf)]
    if s.endswith(".minud"):
        s = s[:-6]
    return s


def _load_manifest(manifest_path: str) -> List[Dict[str, Any]]:
    with open(manifest_path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict) and "instances" in data:
        data = data["instances"]
    if not isinstance(data, list):
        raise RuntimeError("manifest.json must be a list or dict with key 'instances'.")
    return data


def _load_uc_features_npz(npz_path: str) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray]:
    z = np.load(npz_path, allow_pickle=True)
    X = z["features"].astype(np.float32)
    raw_names = [str(x) for x in z["instance_names"].tolist()]
    names = [_norm_inst_name(n) for n in raw_names]

    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-8

    feats_by_name = {names[i]: X[i] for i in range(len(names))}
    return feats_by_name, mu.astype(np.float32), sd.astype(np.float32)


def _load_train_stats_if_present(model_pt_path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    stats_json = str(Path(model_pt_path).parent / "stats.json")
    if not os.path.exists(stats_json):
        return None
    with open(stats_json, "r") as f:
        d = json.load(f)
    mu = np.array(d["mu"], dtype=np.float32)
    sd = np.array(d["sd"], dtype=np.float32)
    return mu, sd


def _infer_dims_from_state_dict(state: Dict[str, torch.Tensor]) -> Tuple[int, int, int]:
    """
    Infer (d_in, hidden, n_classes) from weights.
    For our network:
      net.0.weight shape = (hidden, d_in)
      net.4.weight shape = (n_classes, hidden)
    We do this robustly without assuming exact key names.
    """
    first_w = None
    last_w = None

    # find candidate 2D weights
    weights = [(k, v) for k, v in state.items() if k.endswith("weight") and isinstance(v, torch.Tensor) and v.ndim == 2]
    if not weights:
        raise RuntimeError("No 2D weight matrices found in model state_dict.")

    # pick smallest input-dim weight as "first" (usually hidden x d_in)
    # and largest output-dim that matches hidden as "last"
    # but easiest: just look for (hidden, d_in) then (n_classes, hidden)
    # We'll assume the smallest second-dimension is d_in.
    weights_sorted = sorted(weights, key=lambda kv: kv[1].shape[1])  # sort by in_features
    first_w = weights_sorted[0][1]
    hidden, d_in = first_w.shape

    # find a weight whose in_features == hidden and out_features != hidden (should be last)
    for _, w in weights:
        if w.shape[1] == hidden and w.shape[0] != hidden:
            last_w = w
            break
    if last_w is None:
        # fallback: choose weight with in_features==hidden and maximal out_features
        candidates = [w for _, w in weights if w.shape[1] == hidden]
        if not candidates:
            raise RuntimeError("Could not infer n_classes from model weights (no layer with in_features==hidden).")
        last_w = max(candidates, key=lambda w: w.shape[0])

    n_classes = int(last_w.shape[0])
    return int(d_in), int(hidden), int(n_classes)


def _load_model(model_pt: str, n_classes_expected: int, device: str = "cpu") -> ClassifierMLP:
    state = torch.load(model_pt, map_location=device)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    if not isinstance(state, dict):
        raise RuntimeError("model.pt did not contain a state_dict-like object.")

    d_in, hidden, n_classes = _infer_dims_from_state_dict(state)

    if n_classes != n_classes_expected:
        raise RuntimeError(
            f"Model output classes ({n_classes}) != classes provided ({n_classes_expected}). "
            f"Check your --classes order/length or you loaded the wrong model.pt."
        )

    model = ClassifierMLP(d_in=d_in, hidden=hidden, n_classes=n_classes).to(device)
    model.load_state_dict(state, strict=False)
    model.eval()
    return model


def _load_config_vectors_from_jsonl(results_jsonl: str, sepa_keys: List[str]) -> Dict[str, np.ndarray]:
    cfg: Dict[str, np.ndarray] = {}
    n_read = 0
    with open(results_jsonl, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_read += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            name = row.get("config_name")
            sepa_freq = row.get("sepa_freq", None)
            if not name or not isinstance(sepa_freq, dict):
                continue
            vec = []
            for k in sepa_keys:
                v = sepa_freq.get(k, 0)
                try:
                    fv = float(v)
                except Exception:
                    fv = 0.0
                vec.append(1 if fv > 0 else 0)
            cfg[name] = np.array(vec, dtype=np.int32)

    if not cfg:
        raise RuntimeError(
            f"Could not load any config vectors from {results_jsonl}. "
            f"Read {n_read} lines but found no rows with (config_name, sepa_freq dict)."
        )
    return cfg


def _apply_config(m: pyopt.Model, sepa_keys: List[str], vec01: np.ndarray) -> None:
    for i, k in enumerate(sepa_keys):
        val = int(vec01[i])
        freq = 1 if val == 1 else 0
        m.setParam(f"separating/{k}/freq", freq)


def _solve_once(lp_path: str, time_limit: int, sepa_keys: List[str], cfg_vec: Optional[np.ndarray]) -> Dict[str, Any]:
    m = pyopt.Model()
    m.hideOutput(True)
    m.readProblem(lp_path)
    if cfg_vec is not None:
        _apply_config(m, sepa_keys, cfg_vec)
    m.setParam("limits/time", float(time_limit))
    m.optimize()

    return {
        "status": str(m.getStatus()),
        "solve_time_sec": float(m.getSolvingTime()),
        "nodes": int(m.getNNodes()),
        "lp_iterations": int(m.getNLPIterations()),
        "obj": float(m.getObjVal()) if m.getNSols() > 0 else None,
    }


def _predict_config(model: ClassifierMLP, uc_feat: np.ndarray, mu: np.ndarray, sd: np.ndarray,
                    classes: List[str], device: str) -> Tuple[str, float]:
    """
    Returns (pred_class, confidence) where confidence is softmax prob of pred_class.
    """
    x = (uc_feat.astype(np.float32) - mu) / sd
    tx = torch.tensor(x.reshape(1, -1), dtype=torch.float32, device=device)
    with torch.no_grad():
        logits = model(tx).detach().cpu().numpy().reshape(-1)  # (K,)
    # softmax for confidence
    ex = np.exp(logits - logits.max())
    probs = ex / (ex.sum() + 1e-12)
    j = int(np.argmax(probs))
    return classes[j], float(probs[j])


# -------------------------
# Main
# -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--uc-features-npz", required=True)
    ap.add_argument("--model-pt", required=True)
    ap.add_argument("--classes", required=True, help="Comma-separated classes in SAME order as training")
    ap.add_argument("--baseline-config", required=True)
    ap.add_argument("--results-jsonl", required=True, help="Step3 results.jsonl to get sepa_freq vectors")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--time-limit", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--sepa-keys", default=",".join(SEPA_KEYS_DEFAULT))
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    rng = random.Random(args.seed)

    classes = [c.strip() for c in args.classes.split(",") if c.strip()]
    if not classes:
        raise RuntimeError("No classes provided.")
    sepa_keys = [s.strip() for s in args.sepa_keys.split(",") if s.strip()]

    manifest = _load_manifest(args.manifest)

    feats_by_name, mu_npz, sd_npz = _load_uc_features_npz(args.uc_features_npz)
    train_stats = _load_train_stats_if_present(args.model_pt)
    if train_stats is not None:
        mu, sd = train_stats
    else:
        mu, sd = mu_npz, sd_npz

    device = "cpu"
    model = _load_model(args.model_pt, n_classes_expected=len(classes), device=device)

    cfg_vecs = _load_config_vectors_from_jsonl(args.results_jsonl, sepa_keys=sepa_keys)
    if args.baseline_config not in cfg_vecs:
        raise RuntimeError(f"baseline-config '{args.baseline_config}' not found in results.jsonl configs.")

    # Build pool of (inst_key, lp_path) that exist in uc_features
    pool: List[Tuple[str, str]] = []
    for e in manifest:
        lp_path = e.get("lp_path") or e.get("path") or e.get("lp") or e.get("file")
        inst_name = e.get("instance_name") or e.get("name") or (Path(lp_path).stem if lp_path else None)
        if not lp_path or not inst_name:
            continue
        inst_key = _norm_inst_name(inst_name)
        if inst_key in feats_by_name:
            pool.append((inst_key, lp_path))

    if not pool:
        raise RuntimeError("No manifest entries matched uc_features.npz instance_names (after normalization).")

    rng.shuffle(pool)
    pool = pool[: min(args.n, len(pool))]

    rows: List[Dict[str, Any]] = []
    for inst_key, lp_path in pool:
        uc_feat = feats_by_name[inst_key]

        pred_cfg, conf = _predict_config(model, uc_feat, mu, sd, classes, device)

        if pred_cfg not in cfg_vecs:
            raise RuntimeError(
                f"Predicted config '{pred_cfg}' not found in config vectors from results.jsonl. "
                f"Available include: {sorted(cfg_vecs.keys())[:20]} ..."
            )

        base_vec = cfg_vecs[args.baseline_config]
        pred_vec = cfg_vecs[pred_cfg]

        base_res = _solve_once(lp_path, args.time_limit, sepa_keys, base_vec)
        pred_res = _solve_once(lp_path, args.time_limit, sepa_keys, pred_vec)

        t_base = base_res["solve_time_sec"]
        t_pred = pred_res["solve_time_sec"]
        delta = (t_base - t_pred) / max(t_base, 1e-9)

        rows.append({
            "instance_name": inst_key,
            "lp_path": lp_path,
            "baseline_config": args.baseline_config,
            "pred_config": pred_cfg,
            "pred_conf": conf,
            "baseline_time_sec": t_base,
            "pred_time_sec": t_pred,
            "delta": float(delta),
            "baseline_status": base_res["status"],
            "pred_status": pred_res["status"],
            "baseline_nodes": base_res["nodes"],
            "pred_nodes": pred_res["nodes"],
            "baseline_lp_iterations": base_res["lp_iterations"],
            "pred_lp_iterations": pred_res["lp_iterations"],
        })

        print(f"[{inst_key}] pred={pred_cfg} conf={conf:.3f}  "
              f"t_base={t_base:.3f}s t_pred={t_pred:.3f}s  delta={delta:.4f}")

    out_csv = os.path.join(args.outdir, "online_eval_rows.csv")
    out_json = os.path.join(args.outdir, "online_eval_summary.json")

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    deltas = np.array([r["delta"] for r in rows], dtype=float) if rows else np.array([], dtype=float)
    summary = {
        "n": int(len(rows)),
        "baseline_config": args.baseline_config,
        "classes": classes,
        "sepa_keys": sepa_keys,
        "time_limit": args.time_limit,
        "mean_delta": float(deltas.mean()) if len(deltas) else None,
        "median_delta": float(np.median(deltas)) if len(deltas) else None,
        "pct_positive": float((deltas > 0).mean()) if len(deltas) else None,
    }

    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)

    print("\nWrote:")
    print(f"  {out_csv}")
    print(f"  {out_json}")
    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

