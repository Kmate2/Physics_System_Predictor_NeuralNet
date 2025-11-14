from fastapi import APIRouter, Depends, HTTPException
import numpy as np

from project.backend.schemas import PredictRequest, PredictResponse, Prediction
from project.backend.deps import get_artifacts
from project.backend.predict_utils import predict

router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest, artifacts = Depends(get_artifacts)):
    model, sx, sy, device = artifacts
    X = np.array([[req.velocity, req.angle_deg]], dtype=np.float32)
    try:
        y = predict(model, X, sx, sy, device)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")
    r, h, t = map(float, y[0])
    return PredictResponse(prediction=Prediction(range_m=r, max_height_m=h, flight_time_s=t))
