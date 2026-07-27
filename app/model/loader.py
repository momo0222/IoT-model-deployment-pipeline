from pathlib import Path


def load_model(model_path: str | None):
    """
    Load the model artifact when it exists.

    During setup, the model file may not be available yet. In that case we
    return None so the API, Streamlit app, and Docker environment can still
    run in placeholder mode.

    Once the trained model is ready, replace the final return with the right
    loading call for the artifact format, such as joblib.load(path),
    pickle.load(file), torch.load(path), or mlflow.pyfunc.load_model(path).
    """
    if not model_path:
        return None

    path = Path(model_path)

    if not path.exists():
        return None

    # Temporary placeholder: replace this once the model format is known.
    return path
