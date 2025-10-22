import numpy as np
import torch

@torch.no_grad()
def predict(model, X_new_raw: np.ndarray, scaler_x, scaler_y, device):

    model.eval()
    Xs = scaler_x.transform(X_new_raw.astype(np.float32))
    X = torch.tensor(Xs, dtype=torch.float32, device=device)
    y_s = model(X).cpu().numpy()
    y = scaler_y.inverse_transform(y_s)
    return y