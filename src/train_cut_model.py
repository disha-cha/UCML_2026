#!/usr/bin/env python3
"""
train_cut_model.py

Train a small MLP regressor to predict cut lookahead quality from cut features.

Input .npz (from collect_cut_data.py):
  features   : float32 (N, 8)
  labels     : float32 (N,)  — normalized LP improvement from lookahead

Positive labels = cut improved LP bound (we want to rank these high).
The model predicts a quality score; at inference time the top-k cuts by score
are selected via CutQualitySepa.

Output (to --outdir):
  cut_model.pt  — torch checkpoint with state_dict, mu, sd, d_in, hidden
  cut_metrics.json

Usage:
  python src/train_cut_model.py \\
    --data experiments/step7_cut_data/cut_training_data.npz \\
    --outdir experiments/step7_cut_data/
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn


class CutMLP(nn.Module):
    def __init__(self, d_in: int, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Path to cut_training_data.npz")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    npz = np.load(args.data, allow_pickle=True)
    X = npz["features"].astype(np.float32)
    y = npz["labels"].astype(np.float32)
    feat_names = list(npz["feature_names"])

    print(f"Loaded {X.shape[0]} cut samples, {X.shape[1]} features")
    print(f"Label stats: mean={y.mean():.4f}, std={y.std():.4f}, "
          f"pct_positive={(y > 0).mean():.1%}")

    # Normalize features
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-8
    X_norm = (X - mu) / sd

    # Train/val split
    idx = np.random.permutation(len(X))
    n_val = max(1, int(len(X) * args.val_frac))
    val_idx, train_idx = idx[:n_val], idx[n_val:]

    X_tr = torch.tensor(X_norm[train_idx])
    y_tr = torch.tensor(y[train_idx])
    X_va = torch.tensor(X_norm[val_idx])
    y_va = torch.tensor(y[val_idx])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CutMLP(d_in=X.shape[1], hidden=args.hidden).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    X_tr, y_tr = X_tr.to(device), y_tr.to(device)
    X_va, y_va = X_va.to(device), y_va.to(device)

    best_val_loss = float("inf")
    best_path = outdir / "cut_model.pt"

    for ep in range(1, args.epochs + 1):
        model.train()
        pred = model(X_tr)
        loss = loss_fn(pred, y_tr)
        opt.zero_grad()
        loss.backward()
        opt.step()

        if ep % 20 == 0 or ep == 1:
            model.eval()
            with torch.no_grad():
                val_loss = loss_fn(model(X_va), y_va).item()

            # Ranking metric: NDCG@k for top-10
            with torch.no_grad():
                scores = model(X_va).cpu().numpy()
            true_labels = y_va.cpu().numpy()
            top10 = np.argsort(scores)[-10:]
            pct_pos_top10 = (true_labels[top10] > 0).mean()

            print(f"  ep {ep:4d}  train_loss={loss.item():.6f}  "
                  f"val_loss={val_loss:.6f}  pct_pos@10={pct_pos_top10:.1%}")

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save({
                    "state_dict": model.state_dict(),
                    "d_in": X.shape[1],
                    "hidden": args.hidden,
                    "mu": mu.tolist(),
                    "sd": sd.tolist(),
                    "feat_names": feat_names,
                }, best_path)

    # Final eval
    ckpt = torch.load(best_path, map_location=device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    with torch.no_grad():
        scores = model(X_va).cpu().numpy()
    true_labels = y_va.cpu().numpy()

    k_vals = [5, 10, 20]
    precision_at_k = {}
    for k in k_vals:
        k_actual = min(k, len(scores))
        top_k = np.argsort(scores)[-k_actual:]
        precision_at_k[f"p@{k}"] = float((true_labels[top_k] > 0).mean())

    metrics = {
        "n_train": int(len(train_idx)),
        "n_val": int(n_val),
        "best_val_loss": float(best_val_loss),
        "pct_positive_overall": float((y > 0).mean()),
        **precision_at_k,
        "model_path": str(best_path),
    }
    with open(outdir / "cut_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\nDone.")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
