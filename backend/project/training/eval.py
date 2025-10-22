import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch


def rmse(a, b, axis=0):
    return np.sqrt(np.mean((a - b) ** 2, axis=axis))


def mae(a, b, axis=0):
    return np.mean(np.abs(a - b), axis=axis)


def evaluate(model, loader, sy, device):
    model.eval()
    preds_s, targets_s = [], []
    with torch.no_grad():
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            yhat = model(xb)
            preds_s.append(yhat.cpu().numpy())
            targets_s.append(yb.cpu().numpy())

        preds_s = np.vstack(preds_s)
        targets_s = np.vstack(targets_s)

        preds = sy.inverse_transform(preds_s)
        targets = sy.inverse_transform(targets_s)

        rmse_per = rmse(preds, targets, axis=0).tolist()
        mae_per = mae(preds, targets, axis=0).tolist()
        rmse_all = float(rmse(preds, targets, axis=None))
        mae_all = float(mae(preds, targets, axis=None))

        metrics = {
            "rmse_per_output": {
                "range_m": rmse_per[0],
                "max_height_m": rmse_per[1],
                "flight_time_s": rmse_per[2],
            },
            "mae_per_output": {
                "range_m": mae_per[0],
                "max_height_m": mae_per[1],
                "flight_time_s": mae_per[2],
            },
            "rmse_overall": rmse_all,
            "mae_overall": mae_all,
        }
        return metrics


def plot_history(history, path):
    plt.figure(figsize=(8, 5))
    plt.plot(history["train_loss"], label="Train")
    plt.plot(history["val_loss"], label="Validation")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss (scaled targets)")
    plt.title("Training & Validation Loss")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()