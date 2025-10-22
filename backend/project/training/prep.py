import joblib
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def split_and_scale(df, cfg):
    X = df[["velocity", "angle_deg"]].values.astype(np.float32)
    Y = df[["range", "max_height", "flight_time"]].values.astype(np.float32)

    X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=cfg.test_size, random_state=cfg.seed
    )
    X_train, X_val, Y_train, Y_val = train_test_split(
    X_train, Y_train, test_size=cfg.val_size, random_state=cfg.seed
    )

    sx = StandardScaler().fit(X_train)
    sy = StandardScaler().fit(Y_train)

    X_train_s = sx.transform(X_train).astype(np.float32)
    X_val_s = sx.transform(X_val).astype(np.float32)
    X_test_s = sx.transform(X_test).astype(np.float32)

    Y_train_s = sy.transform(Y_train).astype(np.float32)
    Y_val_s = sy.transform(Y_val).astype(np.float32)
    Y_test_s = sy.transform(Y_test).astype(np.float32)

    joblib.dump(sx, cfg.scaler_x_path)
    joblib.dump(sy, cfg.scaler_y_path)

    return (X_train_s, Y_train_s, X_val_s, Y_val_s, X_test_s, Y_test_s), (sx, sy)


def make_loaders(splits, cfg):
    X_train_s, Y_train_s, X_val_s, Y_val_s, X_test_s, Y_test_s = splits

    train_ds = TensorDataset(torch.tensor(X_train_s), torch.tensor(Y_train_s))
    val_ds = TensorDataset(torch.tensor(X_val_s), torch.tensor(Y_val_s))
    test_ds = TensorDataset(torch.tensor(X_test_s), torch.tensor(Y_test_s))

    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=cfg.num_workers)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)
    test_loader = DataLoader(test_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers)

    return {"train": train_loader, "val": val_loader, "test": test_loader}