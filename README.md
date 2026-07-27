# MLOps model serving template

This project is a small serving stack for a model that will be added later. It has a FastAPI backend for prediction requests and a Streamlit frontend for trying the model from a browser.

The current model code is intentionally a placeholder. The backend and frontend can be tested now, and the model team can plug in the real artifact when it is ready.

## Project layout

```text
.
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── schemas.py
│   ├── model/
│   │   ├── loader.py
│   │   └── predictor.py
│   └── config.py
├── frontend/
│   └── streamlit_app.py
├── models/
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements-api.txt
└── requirements-frontend.txt
```

## What runs where

The FastAPI service owns model loading and prediction:

```text
GET  /health
POST /predict
```

The Streamlit app is only the user interface. It sends JSON to the API and displays the response.

In Docker Compose, the services talk like this:

```text
Streamlit frontend -> http://api:8000 -> FastAPI backend -> model
```

## Run locally with Docker

From the repo root:

```bash
docker compose up --build
```

Open:

```text
Streamlit UI: http://localhost:8501
API docs:    http://localhost:8000/docs
Health:      http://localhost:8000/health
```

Stop everything:

```bash
docker compose down
```

## Run locally without Docker

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements-api.txt
pip install -r requirements-frontend.txt
```

Start the API:

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal, start Streamlit:

```bash
API_URL=http://localhost:8000 streamlit run frontend/streamlit_app.py
```

## Prediction request format

The API expects this shape:

```json
{
  "inputs": {
    "feature_1": 10,
    "feature_2": "example"
  }
}
```

The Streamlit input box should contain only the inner attributes:

```json
{
  "feature_1": 10,
  "feature_2": "example"
}
```

The frontend wraps those attributes as `{"inputs": ...}` before sending the request.

## Model plug-in contract

When the real model is ready, add the artifact here:

```text
models/model.pkl
```

In Docker, that folder is mounted into the API container:

```text
local ./models -> container /app/models
```

The expected model path inside the API container is:

```text
/app/models/model.pkl
```

If the model file has a different name, update `MODEL_PATH` in `docker-compose.yml`.

## Files the model team should update

The main app should not need to change. The model work belongs in these two files:

```text
app/model/loader.py
app/model/predictor.py
```

Use `loader.py` to load the saved artifact.

Example for joblib/scikit-learn-style models:

```python
import joblib

def load_model(model_path: str | None):
    if not model_path:
        return None
    return joblib.load(model_path)
```

Example for pickle:

```python
import pickle

def load_model(model_path: str | None):
    if not model_path:
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)
```

Use `predictor.py` to convert incoming JSON into whatever the model expects.

Example using a fixed feature order:

```python
class Predictor:
    def __init__(self, model):
        self.model = model

    def predict(self, payload: dict) -> dict:
        features = [[
            payload["feature_1"],
            payload["feature_2"],
        ]]

        prediction = self.model.predict(features)

        return {
            "prediction": prediction[0],
            "confidence": None,
            "received_input": payload,
            "model_loaded": self.model is not None,
        }
```

Example using a pandas dataframe:

```python
import pandas as pd

class Predictor:
    def __init__(self, model):
        self.model = model

    def predict(self, payload: dict) -> dict:
        frame = pd.DataFrame([payload])
        prediction = self.model.predict(frame)

        return {
            "prediction": prediction[0],
            "confidence": None,
            "received_input": payload,
            "model_loaded": self.model is not None,
        }
```

## What the model team should provide

Please include these with the model artifact:

- model filename and format
- package versions used to train/save it
- full list of required input attributes
- feature order, if the model depends on order
- allowed values for categorical fields
- expected data types for each field
- one sample input JSON
- expected prediction for that sample

Example attribute contract:

```text
feature_1: number, required
feature_2: string, required, allowed values: example, control, treatment
feature_3: integer, optional, default: 0
```

Example sample input:

```json
{
  "feature_1": 10,
  "feature_2": "example",
  "feature_3": 0
}
```

## Testing the API

Health check:

```bash
curl http://localhost:8000/health
```

Prediction check:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"feature_1": 10, "feature_2": "example"}}'
```

Expected placeholder response before the model is plugged in:

```json
{
  "prediction": "placeholder_prediction",
  "confidence": 1.0,
  "received_input": {
    "feature_1": 10,
    "feature_2": "example"
  },
  "model_loaded": false
}
```

After the model is plugged in, check that:

- `/health` returns `"status": "ok"`
- `/health` returns `"model_loaded": true`
- `/predict` returns the expected sample prediction
- Streamlit shows the same result as the direct API request

## Before pushing to GitHub

Make sure these are not committed:

```text
.venv/
__pycache__/
*.pyc
.env
.DS_Store
```

Large model files should usually not be committed directly. Use Git LFS or external model storage if the artifact is large or private.
