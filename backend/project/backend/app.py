# project/backend/app.py
import os
import logging
from pathlib import Path
import numpy as np
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

from .model_def import ProjectileNet
from .predict_utils import predict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_BASE = os.path.dirname(__file__)
_ARTIFACTS = os.path.abspath(os.path.join(_BASE, "..", "artifacts"))

MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(_ARTIFACTS, "projectile_net.pt"))
SCALER_X_PATH = os.getenv("SCALER_X_PATH", os.path.join(_ARTIFACTS, "projectile_scaler_X.pkl"))
SCALER_Y_PATH = os.getenv("SCALER_Y_PATH", os.path.join(_ARTIFACTS, "projectile_scaler_y.pkl"))

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)
CORS(app)

_artifacts_loaded = False
_artifacts_error = None
model = None
sx = None
sy = None


def _validate_pickle_file(file_path: str, max_size_mb: int = 100) -> None:

    path = Path(file_path)
    
    if not path.exists():
        raise ValueError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"File too large: {size_mb:.2f}MB > {max_size_mb}MB")
    
    if not os.access(file_path, os.R_OK):
        raise ValueError(f"File not readable: {file_path}")
    
    if not path.resolve().is_relative_to(Path(_ARTIFACTS).resolve()):
        raise ValueError(f"File outside artifacts directory: {file_path}")
    
    logger.info(f"Validated pickle file: {file_path} ({size_mb:.2f}MB)")


def _load_artifacts():
    global _artifacts_loaded, _artifacts_error, model, sx, sy
    
    try:
        logger.info("Loading model artifacts...")
        
        # Validate and load scalers
        _validate_pickle_file(SCALER_X_PATH)
        _validate_pickle_file(SCALER_Y_PATH)
        
        sx = joblib.load(SCALER_X_PATH)
        sy = joblib.load(SCALER_Y_PATH)
        logger.info(f"Loaded scalers from {SCALER_X_PATH} and {SCALER_Y_PATH}")
        
        if not os.path.exists(MODEL_PATH):
            raise ValueError(f"Model file not found: {MODEL_PATH}")
        
        model = ProjectileNet()
        state = torch.load(MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state)
        model.to(DEVICE)
        model.eval()
        logger.info(f"Loaded model from {MODEL_PATH} on device {DEVICE}")
        
        _artifacts_loaded = True
        _artifacts_error = None
        
        return model, sx, sy
        
    except Exception as e:
        _artifacts_loaded = False
        _artifacts_error = str(e)
        logger.error(f"Failed to load artifacts: {e}", exc_info=True)
        raise


def _parse_single(payload):

    if isinstance(payload, dict) and "instance" in payload:
        payload = payload["instance"]

    if isinstance(payload, dict):
        v = payload.get("velocity", None)
        a = payload.get("angle_deg", None)
        if v is None or a is None:
            raise ValueError("Missing 'velocity' or 'angle_deg' in payload.")
        
        try:
            v_float = float(v)
            a_float = float(a)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid numeric values: {e}")
        
        if not (0 <= v_float <= 1000):
            raise ValueError(f"Velocity out of range [0, 1000]: {v_float}")
        if not (0 <= a_float <= 90):
            raise ValueError(f"Angle out of range [0, 90]: {a_float}")
            
        return np.asarray([[v_float, a_float]], dtype=np.float32)

    if isinstance(payload, (list, tuple)):
        if len(payload) == 2 and all(isinstance(x, (int, float)) for x in payload):
            v, a = payload
            
            v_float = float(v)
            a_float = float(a)
            
            if not (0 <= v_float <= 1000):
                raise ValueError(f"Velocity out of range [0, 1000]: {v_float}")
            if not (0 <= a_float <= 90):
                raise ValueError(f"Angle out of range [0, 90]: {a_float}")
                
            return np.asarray([[v_float, a_float]], dtype=np.float32)
        raise ValueError("Only a single vector [velocity, angle_deg] is allowed.")

    raise ValueError("Payload must be a dict with velocity/angle_deg or a single list [v, a].")


@app.route("/predict", methods=["POST"])
@torch.no_grad()
def predict_route():

    if not _artifacts_loaded:
        logger.error("Prediction attempted but artifacts not loaded")
        return jsonify({
            "error": "Service not ready",
            "detail": _artifacts_error or "Model artifacts not loaded"
        }), 503
    
    if not request.is_json:
        return jsonify({
            "error": "Invalid content type",
            "detail": "Expected application/json"
        }), 415
    
    try:
        payload = request.get_json(silent=False)
        if payload is None:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        X_raw = _parse_single(payload)
        y = predict(model, X_raw, sx, sy, DEVICE)
        r, h, t = map(float, y[0])
        
        logger.info(f"Prediction successful: velocity={X_raw[0][0]:.2f}, angle={X_raw[0][1]:.2f}")
        
        return jsonify({
            "prediction": {
                "range_m": r,
                "max_height_m": h,
                "flight_time_s": t
            }
        })
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"error": "Validation error", "detail": str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"error": "Prediction failed", "detail": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():

    if _artifacts_loaded:
        return jsonify({
            "status": "healthy",
            "artifacts_loaded": True,
            "device": str(DEVICE),
            "model_path": MODEL_PATH,
            "scaler_x_path": SCALER_X_PATH,
            "scaler_y_path": SCALER_Y_PATH
        }), 200
    else:
        return jsonify({
            "status": "unhealthy",
            "artifacts_loaded": False,
            "error": _artifacts_error,
            "device": str(DEVICE),
            "model_path": MODEL_PATH,
            "scaler_x_path": SCALER_X_PATH,
            "scaler_y_path": SCALER_Y_PATH
        }), 503


try:
    _load_artifacts()
    logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
