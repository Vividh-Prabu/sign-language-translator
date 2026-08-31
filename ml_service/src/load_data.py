import os
import pandas as pd
import numpy as np

def load_processed_dataset(file_path="data/raw/sign_language_data.csv"):
    """
    Loads the sign language dataset from a CSV file.
    Validates file existence, columns, and data types, and removes missing values.
    """
    # 1. Resolve relative paths relative to ml_service root
    if not os.path.isabs(file_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        resolved_path = os.path.join(base_dir, file_path)
    else:
        resolved_path = file_path

    # Check if file exists
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(
            f"Dataset not found at '{resolved_path}'. Please check the file path."
        )
    
    print(f"Loading dataset from: {resolved_path}")
    df = pd.read_csv(resolved_path)
    
    # Check if empty
    if df.empty:
        raise ValueError("The dataset file is empty.")
    
    # Check for target 'label' column
    if 'label' not in df.columns:
        raise ValueError(f"Dataset is missing required 'label' column. Available columns: {list(df.columns)}")
    
    # Handle missing/NaN values
    initial_count = len(df)
    df = df.dropna().reset_index(drop=True)
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        print(f"Cleaned dataset: Removed {dropped_count} row(s) containing missing/NaN values.")
    
    # Separate features (X) and target (y)
    X = df.drop(columns=['label'])
    y = df['label']
    
    # Check for non-numeric feature columns
    non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric_cols:
        raise ValueError(f"Features contain non-numeric columns: {non_numeric_cols}")
    
    print(f"Dataset loaded successfully!")
    print(f"Total valid samples : {X.shape[0]}")
    print(f"Total features       : {X.shape[1]}")
    print(f"Classes found        : {sorted(y.unique().tolist())}")
    
    return X, y

if __name__ == "__main__":
    try:
        X, y = load_processed_dataset()
        print("\nFeatures list:", X.columns.tolist())
    except Exception as e:
        print(f"Error: {e}")