from __future__ import annotations

import os
import time

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .config import PredictiveSettings
from .io_utils import write_json
from .windowing import build_train_valid_windows


class GRURegressor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.gru = nn.GRU(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.gru(x)
        return self.head(output[:, -1, :]).squeeze(-1)


def train_gru(settings: PredictiveSettings) -> dict:
    params = settings.gru_params
    train_seq, valid_seq = build_train_valid_windows(settings, params["window_size"])
    device = torch.device("cpu")

    model = GRURegressor(input_size=len(settings.features), hidden_size=params["hidden_size"]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=params["lr"])
    loss_fn = nn.MSELoss()
    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(train_seq.X), torch.from_numpy(train_seq.y)),
        batch_size=params["batch_size"],
        shuffle=True,
    )

    start = time.perf_counter()
    model.train()
    for _ in range(params["epochs"]):
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            optimizer.step()
    fit_seconds = time.perf_counter() - start

    model.eval()
    inference_start = time.perf_counter()
    with torch.no_grad():
        preds = model(torch.from_numpy(valid_seq.X).to(device)).cpu().numpy()
    inference_seconds = time.perf_counter() - inference_start
    pred_df = valid_seq.meta.copy()
    pred_df["model_name"] = "gru"
    pred_df["y_pred"] = preds
    pred_df["target_policy"] = "rul_capped"
    pred_df.to_parquet(settings.out_dir / "03_valid_predictions_gru_or_tcn.parquet", index=False)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "input_size": len(settings.features),
            "hidden_size": params["hidden_size"],
            "window_size": params["window_size"],
            "features": settings.features,
        },
        settings.models_dir / "gru_or_tcn_model.pt",
    )

    metadata = {
        "model_name": "gru",
        "model_class": "GRURegressor",
        "fit_seconds": fit_seconds,
        "inference_seconds_valid": inference_seconds,
        "ms_per_sample_valid": inference_seconds * 1000 / max(1, int(valid_seq.X.shape[0])),
        "train_windows": int(train_seq.X.shape[0]),
        "valid_windows": int(valid_seq.X.shape[0]),
        "window_size": params["window_size"],
        "features": settings.features,
        "target_cap": settings.target_cap,
        "params": params,
    }
    write_json(settings.out_dir / "03_train_metadata_gru_or_tcn.json", metadata)
    return metadata
