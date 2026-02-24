#!/usr/bin/env python3
"""
train_uc_k1_offline.py

Offline k=1 training on UC instances using:
- results.csv: solve_time per (instance, config)
- uc_features.npz: UC exogenous features per instance (instance_names must match)

We compute per-instance improvement (delta) relative to a baseline config (default: all_off):
    delta(x, s) = (t_base(x) - t_s(x)) / t_base(x)

Then we train an instance -> config classifier over subset A, where label for each instance
is argmax_s delta(x,s) over s in A.  (Simple and robust starting point.)

Outputs written to --outdir:
- dataset_train.csv / dataset_val.csv (assembled training tables)
- model.pt (torch checkpoint)
- metrics.json
- preds_val.csv
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn


# -----------------------------
# Small model: MLP classifier
# -----------------------------

class MLP(nn.Module):
    def __init__(self, d_in: int, n_classes: int, hidden: int = 128, depth: int = 2, dropout: float = 0.1):
        super().__init__()
        layers: List[nn.Module] = []
        d = d_in
        for _ in range(depth):
            layers += [nn.Linear(d, hidden), nn.ReLU(), nn.Dropout(dropout)]
            d = hidden
        layers += [nn.Linear(d, n_classes)]
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class DatasetPack:
    X: np.ndarray
    y: np.ndarray
    inst: List[str]
    y_name: List[str]  # config names aligned with class indices


def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_uc_features(npz_path: str) -> Tuple[Dict[str, np.ndarray], List[str]]:
    npz = np.load(npz_path, allow_pickle=True)
    feats = npz["features"].astype(np.float32)
    names = [str(x) for x in npz["instance_names"].tolist()]
    feat_names = [str(x) for x in npz["feature_names"].tolist()] if "feature_names" in npz.files else []
    return {n: feats[i] for i, n in enumerate(names)}, feat_names


def parse_subset_a(subset_a: str) -> List[str]:
    # allow comma-separated and/or whitespace
    parts = [p.strip() for p in subset_a.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def assemble_table(
    df: pd.DataFrame,
    feat_map: Dict[str, np.ndarray],
    subset_a: List[str],
    baseline_config: str,
) -> pd.DataFrame:
    """
    Build a per-(instance, config) table with features and computed delta.
    Requires:
      df columns: instance_name, config_name, solve_time_sec
    """
    required = {"instance_name", "config_name", "solve_time_sec"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"results.csv missing required columns: {sorted(missing)}")

    # filter to subset A
    df = df[df["config_name"].isin(subset_a)].copy()
    if df.empty:
        raise RuntimeError("After filtering to subset A, results table is empty. Check config_name strings.")

    # baseline times per instance (must exist)
    base = df[df["config_name"] == baseline_config][["instance_name", "solve_time_sec"]].rename(
        columns={"solve_time_sec": "baseline_time_sec"}
    )
    if base.empty:
        raise RuntimeError(
            f"No rows for baseline_config='{baseline_config}' found in results.csv "
            f"(within subset A)."
        )

    df = df.merge(base, on="instance_name", how="inner")

    # compute delta
    df["delta"] = (df["baseline_time_sec"] - df["solve_time_sec"]) / df["baseline_time_sec"]
    df["delta"] = df["delta"].clip(lower=-1.5, upper=1.5)

    # attach features
    X_list = []
    ok = []
    for inst in df["instance_name"].tolist():
        if inst in feat_map:
            X_list.append(feat_map[inst])
            ok.append(True)
        else:
            X_list.append(None)
            ok.append(False)

    df["has_features"] = ok
    df = df[df["has_features"]].copy()
    if df.empty:
        raise RuntimeError(
            "No rows left after matching instance_name to uc_features.npz instance_names."
        )

    X = np.stack([x for x in X_list if x is not None], axis=0).astype(np.float32)
    # because we filtered df after building X_list, rebuild X in same order:
    X = np.stack([feat_map[i] for i in df["instance_name"].tolist()], axis=0).astype(np.float32)

    # expand into columns f0..fD
    for j in range(X.shape[1]):
        df[f"f{j}"] = X[:, j]

    return df


def make_instance_labels(df: pd.DataFrame, subset_a: List[str]) -> pd.DataFrame:
    """
    From per-(instance, config) rows, pick best config per instance via max delta.
    Returns per-instance table with label config_name.
    """
    # choose max-delta row per instance
    best = (
        df.sort_values(["instance_name", "delta"], ascending=[True, False])
          .groupby("instance_name", as_index=False)
          .head(1)
          .copy()
    )
    # Keep only one row per instance with features
    return best


def split_train_val(instances: List[str], val_frac: float = 0.2, seed: int = 42) -> Tuple[set, set]:
    rng = np.random.RandomState(seed)
    inst = np.array(sorted(instances), dtype=object)
    rng.shuffle(inst)
    n_val = max(1, int(len(inst) * val_frac))
    val = set(inst[:n_val].tolist())
    train = set(inst[n_val:].tolist())
    return train, val


def pack_dataset(best_df: pd.DataFrame, subset_a: List[str]) -> DatasetPack:
    # class mapping
    classes = list(subset_a)
    class_to_idx = {c: i for i, c in enumerate(classes)}

    feat_cols = [c for c in best_df.columns if c.startswith("f")]
    X = best_df[feat_cols].to_numpy(dtype=np.float32)
    y = best_df["config_name"].map(class_to_idx).to_numpy(dtype=np.int64)
    inst = best_df["instance_name"].astype(str).tolist()
    return DatasetPack(X=X, y=y, inst=inst, y_name=classes)


def train_classifier(
    train_pack: DatasetPack,
    val_pack: DatasetPack,
    outdir: Path,
    lr: float = 1e-3,
    epochs: int = 200,
    hidden: int = 128,
    depth: int = 2,
    dropout: float = 0.1,
    seed: int = 42,
) -> Dict:
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    d_in = train_pack.X.shape[1]
    n_classes = len(train_pack.y_name)
    model = MLP(d_in, n_classes, hidden=hidden, depth=depth, dropout=dropout).to(device)

    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    Xtr = torch.tensor(train_pack.X, device=device)
    ytr = torch.tensor(train_pack.y, device=device)

    Xva = torch.tensor(val_pack.X, device=device)
    yva = torch.tensor(val_pack.y, device=device)

    best_acc = -1.0
    best_path = outdir / "model.pt"

    for ep in range(1, epochs + 1):
        model.train()
        logits = model(Xtr)
        loss = loss_fn(logits, ytr)
        opt.zero_grad()
        loss.backward()
        opt.step()

        if ep % 10 == 0 or ep == 1:
            model.eval()
            with torch.no_grad():
                pred_tr = logits.argmax(dim=1)
                acc_tr = (pred_tr == ytr).float().mean().item()

                logits_va = model(Xva)
                pred_va = logits_va.argmax(dim=1)
                acc_va = (pred_va == yva).float().mean().item()

            if acc_va > best_acc:
                best_acc = acc_va
                torch.save(
                    {
                        "state_dict": model.state_dict(),
                        "classes": train_pack.y_name,
                        "d_in": d_in,
                        "hidden": hidden,
                        "depth": depth,
                        "dropout": dropout,
                    },
                    best_path,
                )

    # final eval + preds
    ckpt = torch.load(best_path, map_location=device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    with torch.no_grad():
        logits_va = model(Xva)
        probs_va = torch.softmax(logits_va, dim=1).cpu().numpy()
        pred_va = probs_va.argmax(axis=1)

    preds_df = pd.DataFrame(
        {
            "instance_name": val_pack.inst,
            "y_true": [train_pack.y_name[i] for i in val_pack.y],
            "y_pred": [train_pack.y_name[i] for i in pred_va],
            "p_pred": probs_va.max(axis=1),
        }
    )
    preds_df.to_csv(outdir / "preds_val.csv", index=False)

    metrics = {
        "device": str(device),
        "n_train": int(len(train_pack.inst)),
        "n_val": int(len(val_pack.inst)),
        "val_acc": float((preds_df["y_true"] == preds_df["y_pred"]).mean()),
        "classes": train_pack.y_name,
        "model_path": str(best_path),
    }
    return metrics


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results-csv", required=True)
    p.add_argument("--uc-features-npz", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--subset-a", required=True, help="Comma-separated config_name strings (must match results.csv)")
    p.add_argument("--baseline-config", default="all_off", help="config used as baseline for delta")
    p.add_argument("--val-frac", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)

    # training hyperparams
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--hidden", type=int, default=128)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--dropout", type=float, default=0.1)

    args = p.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    subset_a = parse_subset_a(args.subset_a)
    if not subset_a:
        raise RuntimeError("Empty subset A parsed. Provide --subset-a like 'a,b,c'.")

    df = pd.read_csv(args.results_csv)
    feat_map, feat_names = load_uc_features(args.uc_features_npz)

    assembled = assemble_table(df, feat_map, subset_a, baseline_config=args.baseline_config)
    assembled.to_csv(outdir / "dataset_all_rows.csv", index=False)

    best = make_instance_labels(assembled, subset_a)
    if best.empty:
        raise RuntimeError("No per-instance best rows constructed (unexpected).")

    # split by instance
    train_set, val_set = split_train_val(best["instance_name"].tolist(), val_frac=args.val_frac, seed=args.seed)
    train_df = best[best["instance_name"].isin(train_set)].copy()
    val_df = best[best["instance_name"].isin(val_set)].copy()

    train_df.to_csv(outdir / "dataset_train.csv", index=False)
    val_df.to_csv(outdir / "dataset_val.csv", index=False)

    train_pack = pack_dataset(train_df, subset_a)
    val_pack = pack_dataset(val_df, subset_a)

    metrics = train_classifier(
        train_pack=train_pack,
        val_pack=val_pack,
        outdir=outdir,
        lr=args.lr,
        epochs=args.epochs,
        hidden=args.hidden,
        depth=args.depth,
        dropout=args.dropout,
        seed=args.seed,
    )

    with open(outdir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Done.")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
