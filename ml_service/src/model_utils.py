import os
import joblib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

_CACHED_MODEL = None
_CACHED_SCALER = None

def load_model(model_filename="svm_model.pkl"):
    """Loads and caches the trained SVM model."""
    global _CACHED_MODEL
    if _CACHED_MODEL is None:
        model_path = os.path.join(MODELS_DIR, model_filename)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at '{model_path}'. Ensure train_model.py has been executed."
            )
        _CACHED_MODEL = joblib.load(model_path)
    return _CACHED_MODEL

def load_scaler(scaler_filename="scaler.pkl"):
    """Loads and caches the fitted StandardScaler."""
    global _CACHED_SCALER
    if _CACHED_SCALER is None:
        scaler_path = os.path.join(MODELS_DIR, scaler_filename)
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(
                f"Scaler file not found at '{scaler_path}'. Ensure train_model.py has been executed."
            )
        _CACHED_SCALER = joblib.load(scaler_path)
    return _CACHED_SCALER

def save_model(model, model_filename="svm_model.pkl"):
    """Saves a model instance to the models directory."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, model_filename)
    joblib.dump(model, model_path)
    return model_path

def save_scaler(scaler, scaler_filename="scaler.pkl"):
    """Saves a scaler instance to the models directory."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    scaler_path = os.path.join(MODELS_DIR, scaler_filename)
    joblib.dump(scaler, scaler_path)
    return scaler_path