from typing import Optional
from pydantic import BaseModel, Field, confloat

class PredictRequest(BaseModel):
    velocity: confloat(ge=0, le=500) = Field(..., description="m/s")
    angle_deg: confloat(ge=0, le=90) = Field(..., description="degrees")

class Prediction(BaseModel):
    range_m: float
    max_height_m: float
    flight_time_s: float

class PredictResponse(BaseModel):
    prediction: Prediction
    warnings: Optional[dict] = None
