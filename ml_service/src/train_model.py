import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from src.load_data import load_processed_dataset

def train_and_tune_model(file_path="data/raw/sign_language_data.csv", test_size=0.2, random_state=42):
    """
    Complete training pipeline:
    1. Loads dataset
    2. Converts features to NumPy array
    3. Performs stratified train/test split
    4. Fits and saves StandardScaler
    5. Runs GridSearchCV with StratifiedKFold for SVM (RBF)
    6. Saves the best model and test split for evaluation
    """
    # 1. Load Data
    X, y = load_processed_dataset(file_path)
    
    # Extract feature values as pure NumPy array to avoid feature-name discrepancy warnings
    X_arr = X.values if hasattr(X, "values") else np.array(X)
    y_arr = y.values if hasattr(y, "values") else np.array(y)
    
    # 2. Stratified Split
    print("\n--- Train/Test Split ---")
    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr,
        test_size=test_size,
        random_state=random_state,
        stratify=y_arr
    )
    print(f"Training samples: {X_train.shape[0]} | Testing samples: {X_test.shape[0]}")
    
    # 3. Scale Features (Fit only on train)
    print("\n--- Feature Scaling ---")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models_dir = os.path.join(PROJECT_ROOT, "models")
    os.makedirs(models_dir, exist_ok=True)
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"Fitted scaler saved to: {scaler_path}")
    
    # 4. Hyperparameter Tuning using Stratified 5-Fold CV
    print("\n--- Hyperparameter Tuning (SVM with RBF Kernel) ---")
    param_grid = {
        'C': [0.1, 1, 10, 50, 100],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
        'kernel': ['rbf']
    }
    
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    grid_search = GridSearchCV(
        estimator=SVC(probability=True, random_state=random_state),
        param_grid=param_grid,
        cv=cv_strategy,
        scoring='accuracy',
        n_jobs=1,
        verbose=1
    )
    
    print("Running GridSearchCV on training set...")
    grid_search.fit(X_train_scaled, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"\nBest Cross-Validation Score: {grid_search.best_score_:.4f}")
    print(f"Best Hyperparameters: {grid_search.best_params_}")
    
    # 5. Save Model and Test Data
    model_path = os.path.join(models_dir, "svm_model.pkl")
    joblib.dump(best_model, model_path)
    print(f"Trained model saved to: {model_path}")
    
    test_data_path = os.path.join(models_dir, "test_data.pkl")
    joblib.dump((X_test_scaled, y_test, list(X.columns)), test_data_path)
    print(f"Test split saved for evaluation to: {test_data_path}")
    
    return best_model, scaler

if __name__ == "__main__":
    try:
        train_and_tune_model()
        print("\nModel training and hyperparameter tuning completed successfully!")
    except Exception as e:
        print(f"Error during training: {e}")