from fastapi import FastAPI
from app.api.schemas import PredictionRequest, PredictionResponse
from app.config import settings
from app.model.loader import load_model
from app.model.predictor import Predictor

app = FastAPI(title="ML Model API")

model = load_model(settings.model_path)
predictor = Predictor(model)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    result = predictor.predict(request.inputs)
    return result