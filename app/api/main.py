from fastapi import FastAPI
from app.api.schemas import PredictionRequest, PredictionResponse
from app.model.loader import load_model
from app.model.predictor import Predictor

app = FastAPI(title="ML Model API")

attack_model = load_model("attack")
attack_predictor = Predictor(attack_model)

severity_model = load_model("severity")
severity_predictor = Predictor(severity_model)

rf_model = load_model("random_forest")
rf_predictor = Predictor(rf_model)

@app.get("/health_attack")
def health_attack():
    return {
        "status": "ok",
        "model_loaded": attack_model is not None
    }

@app.get("/health_severity")
def health_severity():
    return {
        "status": "ok",
        "model_loaded": severity_model is not None
    }

@app.get("/health_rf")
def health_rf():
    return {
        "status":"ok",
        "model_loaded": rf_model is not None
    }

@app.post("/predict_attack", response_model=PredictionResponse)
def predict_attack(request: PredictionRequest):
    result = attack_predictor.predict(request.inputs)
    return result

@app.post("/predict_severity", response_model=PredictionResponse)
def predict_severity(request: PredictionRequest):
    result = severity_predictor.predict(request.inputs)
    mapping = {0:"CRITICAL",1:"HIGH",2:"LOW",3:"MEDIUM",4:"None",5:"NaN"}
    result["prediction"] = mapping[result["prediction"]]
    return result

@app.post("/predict_rf",response_model=PredictionResponse)
def predict_rf(request: PredictionRequest):
    result = rf_predictor.predict(request.inputs)
    return result