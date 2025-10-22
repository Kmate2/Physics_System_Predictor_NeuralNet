import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
from backend.model_def import ProjectileNet
from backend.predict_utils import predict


def test_predict_single_sample():
    model = ProjectileNet()
    model.eval()


    X_train = np.array([[20, 30], [40, 50], [60, 70]], dtype=np.float32)
    Y_train = np.array([[100, 20, 4], [200, 40, 6], [300, 60, 8]], dtype=np.float32)

    scaler_x = StandardScaler().fit(X_train)
    scaler_y = StandardScaler().fit(Y_train)


    X_new = np.array([[30, 45]], dtype=np.float32)

    device = torch.device("cpu")
    result = predict(model, X_new, scaler_x, scaler_y, device)


    assert result.shape == (1, 3)

    assert not np.isnan(result).any()


def test_predict_multiple_samples():
    model = ProjectileNet()
    model.eval()

    X_train = np.array([[20, 30], [40, 50], [60, 70]], dtype=np.float32)
    Y_train = np.array([[100, 20, 4], [200, 40, 6], [300, 60, 8]], dtype=np.float32)

    scaler_x = StandardScaler().fit(X_train)
    scaler_y = StandardScaler().fit(Y_train)

    X_new = np.array([[30, 45], [50, 60], [70, 75]], dtype=np.float32)

    device = torch.device("cpu")
    result = predict(model, X_new, scaler_x, scaler_y, device)

    assert result.shape == (3, 3)
    assert not np.isnan(result).any()


def test_predict_model_stays_in_eval_mode():
    model = ProjectileNet()
    model.train()  # Set to training mode initially

    X_train = np.array([[20, 30], [40, 50]], dtype=np.float32)
    Y_train = np.array([[100, 20, 4], [200, 40, 6]], dtype=np.float32)

    scaler_x = StandardScaler().fit(X_train)
    scaler_y = StandardScaler().fit(Y_train)

    X_new = np.array([[30, 45]], dtype=np.float32)
    device = torch.device("cpu")

    result = predict(model, X_new, scaler_x, scaler_y, device)

    assert not model.training


def test_predict_with_edge_values():
    model = ProjectileNet()
    model.eval()

    X_train = np.array([[10, 10], [100, 80]], dtype=np.float32)
    Y_train = np.array([[50, 10, 2], [500, 100, 10]], dtype=np.float32)

    scaler_x = StandardScaler().fit(X_train)
    scaler_y = StandardScaler().fit(Y_train)

    X_new = np.array([[10, 10], [100, 80]], dtype=np.float32)
    device = torch.device("cpu")

    result = predict(model, X_new, scaler_x, scaler_y, device)

    assert result.shape == (2, 3)
    assert not np.isnan(result).any()