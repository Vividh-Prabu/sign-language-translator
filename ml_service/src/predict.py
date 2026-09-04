import os
import sys
import warnings

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
from src.model_utils import load_model, load_scaler

def validate_and_format_input(features, scaler):
    expected_count = scaler.n_features_in_
    feature_names = getattr(scaler, "feature_names_in_", None)

    if isinstance(features, (list, tuple)):
        features_array = np.array(features, dtype=float)
    elif isinstance(features, pd.DataFrame):
        features_array = features.to_numpy(dtype=float)
    elif isinstance(features, pd.Series):
        features_array = features.to_numpy(dtype=float)
    elif isinstance(features, np.ndarray):
        features_array = features.astype(float)
    else:
        raise TypeError(f"Invalid input type: {type(features)}")

    if features_array.ndim == 1:
        features_array = features_array.reshape(1, -1)
    elif features_array.ndim > 2 or features_array.shape[0] != 1:
        raise ValueError(f"Invalid input shape {features_array.shape}. Expected (1, {expected_count}).")

    if features_array.shape[1] != expected_count:
        raise ValueError(f"Feature count mismatch: received {features_array.shape[1]}, expected {expected_count}")

    if np.isnan(features_array).any() or np.isinf(features_array).any():
        raise ValueError("Input features contain NaN or Infinite values.")

    if feature_names is not None:
        return pd.DataFrame(features_array, columns=feature_names)
    return features_array

def predict_gesture(features):
    model = load_model()
    scaler = load_scaler()
    validated_df = validate_and_format_input(features, scaler)
    scaled_features = scaler.transform(validated_df)
    prediction = model.predict(scaled_features)
    return str(prediction[0])

def predict_gesture_with_confidence(features):
    model = load_model()
    scaler = load_scaler()
    validated_df = validate_and_format_input(features, scaler)
    scaled_features = scaler.transform(validated_df)

    prediction = model.predict(scaled_features)[0]
    probabilities = model.predict_proba(scaled_features)[0]
    class_idx = np.where(model.classes_ == prediction)[0][0]
    confidence = float(probabilities[class_idx])

    return str(prediction), confidence

def predict_gesture_top_distribution(features, top_n=5):
    model = load_model()
    scaler = load_scaler()
    validated_df = validate_and_format_input(features, scaler)
    scaled_features = scaler.transform(validated_df)

    prediction = model.predict(scaled_features)[0]
    probabilities = model.predict_proba(scaled_features)[0]
    
    sorted_indices = np.argsort(probabilities)[::-1]
    top_distribution = [
        {"label": str(model.classes_[i]), "prob": round(float(probabilities[i]) * 100, 2)}
        for i in sorted_indices[:top_n]
    ]
    
    top_confidence = top_distribution[0]["prob"]
    return str(prediction), top_confidence, top_distribution
