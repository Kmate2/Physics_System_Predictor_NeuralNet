import os
import json
import random
import logging
from dataclasses import dataclass, asdict

import numpy as np
import torch
import torch.nn as nn

from backend.model_def import ProjectileNet
from training.data import load_or_simulate_dataframe
from training.prep import split_and_scale, make_loaders
from training.eval import evaluate, plot_history

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    batch_size: int = 64
    epochs: int = 500
    lr: float = 1e-3
    patience: int = 40
    seed: int = 42
    val_size: float = 0.2
    test_size: float = 0.2
    num_workers: int = 0

    data_path: str = "./artifacts/projectile_dataset.csv"
    model_path: str = "./artifacts/projectile_net.pt"
    scaler_x_path: str = "./artifacts/projectile_scaler_X.pkl"
    scaler_y_path: str = "./artifacts/projectile_scaler_y.pkl"
    metrics_path: str = "./artifacts/projectile_metrics.json"
    curve_png_path: str = "./artifacts/training_curve.png"


CFG = Config()


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_model(model, loaders, cfg: Config, device):
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    best_val = float("inf")
    best_epoch = -1
    epochs_no_improve = 0
    history = {"train_loss": [], "val_loss": []}

    for epoch in range(1, cfg.epochs + 1):

        model.train()
        running = 0.0
        n = 0
        for xb, yb in loaders["train"]:
            xb = xb.to(device)
            yb = yb.to(device)

            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()

            bs = xb.size(0)
            running += loss.item() * bs
            n += bs
        train_loss = running / max(1, n)


        model.eval()
        running_v = 0.0
        nv = 0
        with torch.no_grad():
            for xb, yb in loaders["val"]:
                xb = xb.to(device)
                yb = yb.to(device)
                preds = model(xb)
                loss = criterion(preds, yb)
                bs = xb.size(0)
                running_v += loss.item() * bs
                nv += bs
            val_loss = running_v / max(1, nv)

            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)

            improved = val_loss < best_val - 1e-12
            if improved:
                best_val = val_loss
                best_epoch = epoch
                epochs_no_improve = 0
                os.makedirs(os.path.dirname(cfg.model_path), exist_ok=True)
                torch.save(model.state_dict(), cfg.model_path)
            else:
                epochs_no_improve += 1
            if epoch % 10 == 0 or epoch == 1:
                logger.info(f"Epoch {epoch:4d} - train_loss={train_loss:.6f} val_loss={val_loss:.6f} (best @ {best_epoch}: {best_val:.6f})")

            if epochs_no_improve >= cfg.patience:
                logger.info(f"Early stopping: No improvement for {cfg.patience} epochs. Best val at epoch {best_epoch}.")
                break

    if os.path.exists(cfg.model_path):
        model.load_state_dict(torch.load(cfg.model_path, map_location=device))
    return history, best_epoch, best_val

def main():
    cfg = CFG
    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")


    df = load_or_simulate_dataframe(cfg.data_path)


    splits, scalers = split_and_scale(df, cfg)
    loaders = make_loaders(splits, cfg)
    sx, sy = scalers

    model = ProjectileNet().to(device)

    history, best_epoch, best_val = train_model(model, loaders, cfg, device)

    os.makedirs(os.path.dirname(cfg.curve_png_path), exist_ok=True)
    plot_history(history, cfg.curve_png_path)


    metrics = evaluate(model, loaders["test"], sy, device)


    meta = {
        "config": asdict(cfg),
        "device": str(device),
        "best_epoch": best_epoch,
        "best_val_loss_scaled": best_val,
        "test_metrics": metrics,
    }
    os.makedirs(os.path.dirname(cfg.metrics_path), exist_ok=True)
    with open(cfg.metrics_path, "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Training complete - Best epoch: {best_epoch}")
    logger.info(f"Artifacts saved:")
    logger.info(f"  Model: {cfg.model_path}")
    logger.info(f"  ScalerX: {cfg.scaler_x_path}")
    logger.info(f"  ScalerY: {cfg.scaler_y_path}")
    logger.info(f"  Metrics: {cfg.metrics_path}")
    logger.info(f"  Curve: {cfg.curve_png_path}")

if __name__ == "__main__":
    main()
