"""
load_data.py
------------
Loads the raw sign-language dataset and prints a full inspection report:
shape, columns, dtypes, missing values, duplicates, label balance, and stats.

READ-ONLY: this never changes the raw file. Cleaning happens later in
preprocessing.py.
"""

from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path("data/raw/sign_language_data.csv")


def load_dataset(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the CSV into a pandas DataFrame."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            "Run 'python generate_sample_data.py' first to create it."
        )
    return pd.read_csv(path)


def inspect_dataset(df: pd.DataFrame) -> None:
    """Print a full inspection report about the dataset."""
    print("=" * 60)
    print("DATASET INSPECTION REPORT")
    print("=" * 60)

    print(f"\nRows:    {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    print(list(df.columns))

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values per column:")
    print(df.isna().sum())
    print(f"\nTotal missing cells: {int(df.isna().sum().sum())}")

    print(f"\nDuplicate rows: {int(df.duplicated().sum())}")

    if "label" in df.columns:
        labels = sorted(df["label"].unique())
        print(f"\nUnique labels ({len(labels)}): {labels}")
        print("\nSamples per label:")
        print(df["label"].value_counts().sort_index())
    else:
        print("\nWARNING: no 'label' column found!")

    print("\nBasic statistics (numeric columns):")
    print(df.describe().T)

    print("\n" + "=" * 60)
    print("END OF REPORT")
    print("=" * 60)


if __name__ == "__main__":
    data = load_dataset()
    inspect_dataset(data)