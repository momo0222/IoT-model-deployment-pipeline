from pydantic import BaseModel
from typing import Any

class PredictionRequest(BaseModel):
    inputs: dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: Any
    confidence: float | None = None
    received_input: dict[str, Any] | None = None
    model_loaded: bool