import os
import sys
import json
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
from joblib import parallel_backend
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from src.load_data import load_processed_dataset

def train_and_tune_model(
    file_path="data/raw/sign_language_data.csv",
    test_size=0.2,
    max_samples_per_class=600,
    random_state=42
):
    print(f"Loading merged dataset from: {file_path}")
    X_df, y_df = load_processed_dataset(file_path)
    feature_names = list(X_df.columns)
    
    # Balanced stratified subsampling per class for speed
    print(f"\nBalancing dataset (capping at max {max_samples_per_class} samples/class)...")
    sampled_indices = []
    unique_labels = y_df.unique()
    for lbl in unique_labels:
        cls_idx = y_df[y_df == lbl].index
        if len(cls_idx) > max_samples_per_class:
            chosen = np.random.choice(cls_idx, size=max_samples_per_class, replace=False)
        else:
            chosen = cls_idx.values
        sampled_indices.extend(chosen)
        
    X_balanced = X_df.loc[sampled_indices].reset_index(drop=True)
    y_balanced = y_df.loc[sampled_indices].reset_index(drop=True)
    
    print(f"Total training dataset size: {len(X_balanced)} rows across {len(unique_labels)} classes.")
    print(f"Feature count: {len(feature_names)}")

    X_arr = X_balanced.values
    y_arr = y_balanced.values

    # Stratified Train/Test Split
    print("\n--- Train/Test Split ---")
    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr,
        test_size=test_size,
        random_state=random_state,
        stratify=y_arr
    )
    print(f"Training samples: {X_train.shape[0]} | Testing samples: {X_test.shape[0]}")

    # Feature Scaling
    print("\n--- Feature Scaling ---")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models_dir = os.path.join(PROJECT_ROOT, "models")
    os.makedirs(models_dir, exist_ok=True)
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"Fitted scaler saved to: {scaler_path}")

    # Hyperparameter Optimization (SVM-RBF)
    print("\n--- Hyperparameter Tuning (SVM with RBF Kernel) ---")
    param_grid = {
        'C': [1, 10, 50],
        'gamma': ['scale', 'auto', 0.01],
        'kernel': ['rbf']
    }

    cv_strategy = StratifiedKFold(n_splits=3, shuffle=True, random_state=random_state)
    grid_search = GridSearchCV(
        estimator=SVC(probability=True, random_state=random_state),
        param_grid=param_grid,
        cv=cv_strategy,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )

    print("Running multi-core GridSearchCV...")
    with parallel_backend('threading'):
        grid_search.fit(X_train_scaled, y_train)

    best_model = grid_search.best_estimator_
    print(f"\nBest Cross-Validation Score: {grid_search.best_score_:.4f}")
    print(f"Best Hyperparameters: {grid_search.best_params_}")

    # Save Best Model & Test Set
    model_path = os.path.join(models_dir, "svm_model.pkl")
    joblib.dump(best_model, model_path)
    print(f"Trained model saved to: {model_path}")

    test_data_path = os.path.join(models_dir, "test_data.pkl")
    joblib.dump((X_test_scaled, y_test, feature_names), test_data_path)
    print(f"Test split saved to: {test_data_path}")

    # Metadata Manifest
    metadata = {
        "model_type": "Support Vector Machine (SVC)",
        "kernel": "RBF (Radial Basis Function)",
        "best_hyperparameters": grid_search.best_params_,
        "cross_validation_accuracy": round(float(grid_search.best_score_), 4),
        "total_features": len(feature_names),
        "feature_names": feature_names,
        "classes": sorted(list(np.unique(y_arr))),
        "training_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Model manifest saved to: {metadata_path}")

    return best_model, scaler

if __name__ == "__main__":
    try:
        train_and_tune_model()
        print("\nTraining completed successfully!")
    except Exception as e:
        print(f"Training error: {e}")
