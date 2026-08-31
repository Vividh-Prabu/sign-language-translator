import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
from src.model_utils import load_model, load_scaler

def validate_and_format_input(features, expected_feature_count):
    """
    Validates input features and formats them into a 2D numpy array of shape (1, n_features).
    Raises descriptive ValueError or TypeError on invalid input.
    """
    # 1. Type validation and conversion
    if isinstance(features, (list, tuple)):
        features_array = np.array(features, dtype=float)
    elif isinstance(features, pd.DataFrame):
        features_array = features.to_numpy(dtype=float)
    elif isinstance(features, pd.Series):
        features_array = features.to_numpy(dtype=float)
    elif isinstance(features, np.ndarray):
        features_array = features.astype(float)
    else:
        raise TypeError(
            f"Invalid input type: {type(features)}. Expected list, tuple, np.ndarray, or pd.DataFrame."
        )

    # 2. Reshape to 2D (1, n_features) if 1D input was passed
    if features_array.ndim == 1:
        features_array = features_array.reshape(1, -1)
    elif features_array.ndim > 2 or features_array.shape[0] != 1:
        raise ValueError(
            f"Invalid input shape {features_array.shape}. Expected a single sample with shape (1, {expected_feature_count}) or ({expected_feature_count},)."
        )

    # 3. Feature count validation
    if features_array.shape[1] != expected_feature_count:
        raise ValueError(
            f"Feature count mismatch: received {features_array.shape[1]} features, "
            f"but model requires exactly {expected_feature_count} features."
        )

    # 4. Check for NaN or Inf values
    if np.isnan(features_array).any():
        raise ValueError("Input features contain NaN (missing) values.")
    if np.isinf(features_array).any():
        raise ValueError("Input features contain infinite (Inf) values.")

    return features_array

def predict_gesture(features):
    """
    Public API function for GUI / Application integration.
    
    Parameters:
        features (list, np.ndarray, pd.DataFrame): 12 sensor values.
        
    Returns:
        str: Predicted sign language label (e.g. 'A', 'B', 'SPACE', 'DELETE').
    """
    # Load cached artifacts
    model = load_model()
    scaler = load_scaler()
    expected_count = scaler.n_features_in_

    # Validate and standardize input shape
    validated_features = validate_and_format_input(features, expected_count)

    # Scale features using pre-fitted scaler
    scaled_features = scaler.transform(validated_features)

    # Predict class
    prediction = model.predict(scaled_features)
    
    return str(prediction[0])

def predict_gesture_with_confidence(features):
    """
    Optional helper function returning both the predicted label and the model's confidence score.
    """
    model = load_model()
    scaler = load_scaler()
    expected_count = scaler.n_features_in_

    validated_features = validate_and_format_input(features, expected_count)
    scaled_features = scaler.transform(validated_features)

    prediction = model.predict(scaled_features)[0]
    probabilities = model.predict_proba(scaled_features)[0]
    class_idx = np.where(model.classes_ == prediction)[0][0]
    confidence = float(probabilities[class_idx])

    return str(prediction), confidence

if __name__ == "__main__":
    # Test execution with a dummy valid 12-feature sample
    sample_features = [0.12, 0.45, 0.32, 0.11, 0.09, 9.81, 0.02, 0.15, 1.2, 0.3, 0.5, 25.4]
    
    print("Testing programmatic prediction engine:")
    try:
        pred_label = predict_gesture(sample_features)
        pred_label, conf = predict_gesture_with_confidence(sample_features)
        print(f"Input features        : {sample_features}")
        print(f"Predicted Sign Label  : '{pred_label}'")
        print(f"Confidence Score      : {conf * 100:.2f}%")
        print("Prediction engine works successfully!")
    except Exception as e:
        print(f"Prediction error: {e}")