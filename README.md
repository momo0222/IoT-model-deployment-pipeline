# MLOps model serving template

This project is a small serving stack for an IoT/network intrusion model suite. It has a FastAPI backend for prediction requests and a Streamlit frontend for trying the models from a browser.

Three trained artifacts are committed at the repo root and loaded by the API:

```text
attack_pipeline.joblib     # text -> attack type classifier
severity_pipeline.joblib   # text -> severity classifier
type_random_forest.pkl     # structured network features -> attack type (random forest)
```

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
├── attack_pipeline.joblib
├── severity_pipeline.joblib
├── type_random_forest.pkl
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
├── render.yaml
├── requirements-api.txt
└── requirements-frontend.txt
```

## What runs where

The FastAPI service owns model loading and prediction:

```text
GET  /health            # aggregate status of all three models
GET  /health_attack
GET  /health_severity
GET  /health_rf
POST /predict_attack    # {"inputs": {"DESCRIPTION": "..."}}
POST /predict_severity  # {"inputs": {"DESCRIPTION": "..."}}
POST /predict_rf        # {"inputs": {<32 network feature fields>}}
```

The Streamlit app is only the user interface. It sends JSON to the API (server-side, via `requests`) and displays the response. Because the call happens server-side rather than from the browser, no CORS configuration is needed on the API.

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

## Deploying

### Backend on Render

`render.yaml` at the repo root is a Render Blueprint that builds `Dockerfile.api` as a web service with a `/health` health check.

1. Push this repo to GitHub.
2. In the Render dashboard: **New > Blueprint**, connect the repo, and Render will pick up `render.yaml`.
3. Wait for the build to finish, then confirm `https://<your-service>.onrender.com/health` returns `{"status": "ok", ...}`.

The free Render plan spins the service down after inactivity, so the first request after idle time will be slow while it cold-starts.

### Frontend on Streamlit Community Cloud

1. Push this repo to GitHub (same repo is fine).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at this repo, branch, and `frontend/streamlit_app.py` as the entry point. Streamlit Cloud installs `requirements-frontend.txt` automatically (it looks for that name, or `requirements.txt`, at the app's root).
3. In the app's **Settings > Secrets**, add:
   ```toml
   API_URL = "https://<your-service>.onrender.com"
   ```
4. Deploy. `frontend/streamlit_app.py` reads `API_URL` from `st.secrets` when present (Streamlit Cloud) and falls back to the `API_URL` environment variable otherwise (local/Docker runs).

## Model loading

`app/model/loader.py` loads the three artifacts by their fixed filenames at the project root — no `MODEL_PATH` configuration is needed. `app/model/predictor.py` wraps each model: text-based models (`attack`, `severity`) expect a `DESCRIPTION` field and call `.predict([text])`; the random forest model expects a single-row DataFrame built from the request's `inputs`.

The random forest pipeline requires all 32 fields it was trained on. Fields it doesn't have a value for should be sent as JSON `null` (not `"-"` or empty string) — the pipeline's imputer only treats an actual missing value as "use the most common training value"; any other unseen string is encoded as an out-of-vocabulary category, which is a different codepath.

`scikit-learn` is pinned to `==1.7.2` in `requirements-api.txt` to match the version the pipelines were trained/saved with. Bumping it isn't safe to do casually — a newer scikit-learn release changed an internal `SimpleImputer` attribute name and broke the random forest pipeline's imputation step outright (`AttributeError: 'SimpleImputer' object has no attribute '_fill_dtype'`) when tested during deployment setup. If you need a newer scikit-learn, re-save the pipelines with it first and re-verify `/predict_rf` end to end.

## Testing the API

Health check:

```bash
curl http://localhost:8000/health
```

Prediction check:

```bash
curl -X POST http://localhost:8000/predict_attack \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"DESCRIPTION": "This is a DDOS attack."}}'
```

After deploying, check that:

- `/health` returns `"status": "ok"` with all three models `true`
- `/predict_attack`, `/predict_severity`, `/predict_rf` each return a real prediction (not a 500)
- Streamlit shows the same results as calling the API directly

## Before pushing to GitHub

Make sure these are not committed:

```text
.venv/
__pycache__/
*.pyc
.env
.DS_Store
```
