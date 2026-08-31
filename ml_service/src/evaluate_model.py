import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

def evaluate_saved_model():
    """
    Loads saved model, scaler, and test split, evaluates performance on unseen test data,
    and generates a readable confusion matrix visualization.
    """
    models_dir = os.path.join(PROJECT_ROOT, "models")
    model_path = os.path.join(models_dir, "svm_model.pkl")
    test_data_path = os.path.join(models_dir, "test_data.pkl")
    figures_dir = os.path.join(PROJECT_ROOT, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Validate required artifacts exist
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at '{model_path}'. Run train_model.py first.")
    if not os.path.exists(test_data_path):
        raise FileNotFoundError(f"Test data split not found at '{test_data_path}'. Run train_model.py first.")
        
    print("Loading trained model and test split...")
    model = joblib.load(model_path)
    X_test_scaled, y_test, feature_names = joblib.load(test_data_path)
    
    # 2. Run Inference on Test Data
    y_pred = model.predict(X_test_scaled)
    classes = np.unique(np.concatenate((y_test, y_pred)))
    
    # 3. Calculate Evaluation Metrics
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print("\n==================================================")
    print("           MODEL TEST EVALUATION RESULTS          ")
    print("==================================================")
    print(f"Test Accuracy        : {acc * 100:.2f}%")
    print(f"Macro Precision      : {prec_macro:.4f}")
    print(f"Macro Recall         : {rec_macro:.4f}")
    print(f"Macro F1-Score       : {f1_macro:.4f}")
    print(f"Weighted F1-Score    : {f1_weighted:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, digits=4, zero_division=0))
    
    # 4. Generate & Save Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot(cmap=plt.cm.Blues, ax=ax, values_format='d')
    plt.title("Sign Language SVM - Test Confusion Matrix", fontsize=14, pad=15)
    plt.tight_layout()
    
    cm_path = os.path.join(figures_dir, "test_confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"Confusion matrix plot saved to: {cm_path}")
    print("==================================================")
    
    return {
        "accuracy": acc,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted
    }

if __name__ == "__main__":
    try:
        evaluate_saved_model()
    except Exception as e:
        print(f"Error during model evaluation: {e}")