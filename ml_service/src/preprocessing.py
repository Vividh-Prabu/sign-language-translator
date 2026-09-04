import numpy as np
import pandas as pd

def clean_raw_data(df: pd.DataFrame, drop_duplicates: bool = False) -> pd.DataFrame:
    """
    Cleans raw sensor inputs:
    - Removes rows with all NaN entries
    - Replaces infinite values with NaN and removes them
    - Strips and standardizes gesture labels
    """
    df_clean = df.copy()
    
    # Standardize label column name if present
    for col in ["class", "Class", "target", "Target"]:
        if col in df_clean.columns and "label" not in df_clean.columns:
            df_clean.rename(columns={col: "label"}, inplace=True)
            break

    if "label" in df_clean.columns:
        df_clean["label"] = df_clean["label"].astype(str).str.strip().str.upper()

    # Drop fully empty rows
    df_clean.dropna(how="all", inplace=True)

    # Handle Inf and -Inf
    df_clean.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_clean.dropna(inplace=True)

    if drop_duplicates:
        df_clean.drop_duplicates(inplace=True)

    return df_clean.reset_index(drop=True)

def remove_sensor_outliers(df: pd.DataFrame, factor: float = 3.0) -> pd.DataFrame:
    """
    Applies statistical IQR boundary clipping to suppress transient sensor voltage spikes.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_filtered = df.copy()

    for col in numeric_cols:
        q1 = df_filtered[col].quantile(0.25)
        q3 = df_filtered[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (factor * iqr)
        upper_bound = q3 + (factor * iqr)
        df_filtered[col] = df_filtered[col].clip(lower_bound, upper_bound)

    return df_filtered

def split_features_and_labels(df: pd.DataFrame, label_column: str = "label"):
    """
    Extracts feature matrix X and target label vector y.
    """
    if label_column not in df.columns:
        raise KeyError(f"Label column '{label_column}' not found in DataFrame.")
        
    X = df.drop(columns=[label_column])
    y = df[label_column]
    return X, y
