import numpy as np
import pandas as pd

def extract_motion_magnitudes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes resultant Euclidean vector magnitudes for 3-axis Accelerometer & Gyroscope channels.
    """
    df_feat = df.copy()

    # Accelerometer Magnitude
    acc_cols = [c for c in df_feat.columns if "acc" in c.lower() or "ax" in c.lower() or "ay" in c.lower() or "az" in c.lower()]
    if len(acc_cols) >= 3:
        x, y, z = acc_cols[:3]
        df_feat["acc_magnitude"] = np.sqrt(df_feat[x]**2 + df_feat[y]**2 + df_feat[z]**2)

    # Gyroscope Magnitude
    gyro_cols = [c for c in df_feat.columns if "gyro" in c.lower() or "gx" in c.lower() or "gy" in c.lower() or "gz" in c.lower()]
    if len(gyro_cols) >= 3:
        gx, gy, gz = gyro_cols[:3]
        df_feat["gyro_magnitude"] = np.sqrt(df_feat[gx]**2 + df_feat[gy]**2 + df_feat[gz]**2)

    return df_feat

def extract_flex_finger_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes statistical spread across flex sensors (mean, std dev, min-max range)
    to capture hand curvature posture.
    """
    df_feat = df.copy()
    flex_cols = [c for c in df_feat.columns if "flex" in c.lower() or "sensor" in c.lower()]

    if len(flex_cols) >= 2:
        df_feat["flex_mean"] = df_feat[flex_cols].mean(axis=1)
        df_feat["flex_std"] = df_feat[flex_cols].std(axis=1).fillna(0)
        df_feat["flex_range"] = df_feat[flex_cols].max(axis=1) - df_feat[flex_cols].min(axis=1)

    return df_feat

def apply_full_feature_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executes the end-to-end feature extraction pipeline on any input DataFrame.
    """
    df_trans = extract_motion_magnitudes(df)
    df_trans = extract_flex_finger_ratios(df_trans)
    return df_trans
