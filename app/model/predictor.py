import pandas as pd


class Predictor:
    """
    Stable prediction wrapper.

    FastAPI talks to this instead of directly to the model
    """

    def __init__(self, model):
        self.model = model
    
    def predict(self, payload: dict) -> dict:
        if "DESCRIPTION" in payload.keys():
            text = payload["DESCRIPTION"]
            pred = self.model.predict([text])[0]
        else:
            X = pd.DataFrame([payload])
            pred = self.model.predict(X)[0]

        if hasattr(pred, "item"):
            pred = pred.item()

        return {
            "prediction": pred,
            "confidence": 1.0,
            "received_input": payload,
            "model_loaded": self.model is not None
        }