from pathlib import Path
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def load_model(type:str):
    """
    Load NLP model artifact when it exists.
    """
    try:
        if type=="attack":
            model = joblib.load(PROJECT_ROOT / 'attack_pipeline.joblib')
        elif type=="severity":
            model = joblib.load(PROJECT_ROOT / 'severity_pipeline.joblib')
        elif type=="random_forest":
            model = joblib.load(PROJECT_ROOT / 'type_random_forest.pkl')
    except:
        model = None

    # Temporary placeholder: replace this once the model format is known.
    return model
