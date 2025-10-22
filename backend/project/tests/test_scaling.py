import numpy as np
from sklearn.preprocessing import StandardScaler

def test_scaler_roundtrip():
    X = np.array([[10, 30], [20, 40], [30, 50]], dtype=np.float32)
    sx = StandardScaler().fit(X)
    Xs = sx.transform(X)
    X_back = sx.inverse_transform(Xs)
    assert np.allclose(X_back, X, atol=1e-6)
