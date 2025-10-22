# project/backend/app.py
import os
import numpy as np
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

from .model_def import ProjectileNet
from .predict_utils import predict

_BASE = os.path.dirname(__file__)
_ARTIFACTS = os.path.abspath(os.path.join(_BASE, "..", "artifacts"))

MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(_ARTIFACTS, "projectile_net.pt"))
SCALER_X_PATH = os.getenv("SCALER_X_PATH", os.path.join(_ARTIFACTS, "projectile_scaler_X.pkl"))
SCALER_Y_PATH = os.getenv("SCALER_Y_PATH", os.path.join(_ARTIFACTS, "projectile_scaler_y.pkl"))

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)
CORS(app)

try:
    sx = joblib.load(SCALER_X_PATH)
    sy = joblib.load(SCALER_Y_PATH)
except Exception as e:
    raise SystemExit(f"[FATAL] Could not load scalers: {e}. Train first or point env vars to valid files.")

try:
    model = ProjectileNet()
    state = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(state)
    model.to(DEVICE)
    model.eval()
except Exception as e:
    raise SystemExit(f"[FATAL] Could not load model: {e}. Train first or point env vars to valid file.")

def _parse_single(payload):

    if isinstance(payload, dict) and "instance" in payload:
        payload = payload["instance"]

    if isinstance(payload, dict):
        v = payload.get("velocity", None)
        a = payload.get("angle_deg", None)
        if v is None or a is None:
            raise ValueError("Missing 'velocity' or 'angle_deg'.")
        return np.asarray([[float(v), float(a)]], dtype=np.float32)

    if isinstance(payload, (list, tuple)):

        if len(payload) == 2 and all(isinstance(x, (int, float)) for x in payload):
            v, a = payload
            return np.asarray([[float(v), float(a)]], dtype=np.float32)
        raise ValueError("Only a single vector [velocity, angle_deg] is allowed.")

    raise ValueError("Payload must be a dict with velocity/angle_deg or a single list [v, a].")

@app.route("/predict", methods=["POST"])
@torch.no_grad()
def predict_route():
    try:
        payload = request.get_json(force=True, silent=False)
        X_raw = _parse_single(payload)
        y = predict(model, X_raw, sx, sy, DEVICE)
        r, h, t = map(float, y[0])
        return jsonify({
            "prediction": {
                "range_m": r,
                  "max_height_m": h,
                "flight_time_s": t
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "device": str(DEVICE), "model_path": MODEL_PATH})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
