import os
import sys
import glob
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
OUTPUT_PATH = os.path.join(RAW_DATA_DIR, "sign_language_data.csv")

def extract_label_from_filename_or_folder(filepath):
    """
    Extracts the gesture label (e.g., 'A', 'B', 'SPACE') 
    from the file name or folder structure.
    """
    filename = os.path.splitext(os.path.basename(filepath))[0]
    
    # Common naming patterns: "A_sample1.csv", "gesture_A.csv", "A.csv"
    parts = filename.replace("-", "_").split("_")
    
    # If the file is just named "A.csv"
    if len(filename) <= 3 and filename.isalpha():
        return filename.upper()
    
    # Check parts for alphabetical character or label tag
    for part in parts:
        if len(part) == 1 and part.isalpha():
            return part.upper()
        if part.upper() in ["SPACE", "DELETE", "NOTHING"]:
            return part.upper()
            
    # Fallback: check parent directory name (e.g. data/raw/A/sample1.csv)
    parent_folder = os.path.basename(os.path.dirname(filepath))
    if len(parent_folder) <= 3:
        return parent_folder.upper()
        
    return parts[0].upper()

def merge_csv_files(input_directory=None):
    """
    Finds all CSV files inside data/raw (including subdirectories),
    merges them into a single dataframe, attaches the 'label' column,
    and saves it to data/raw/sign_language_data.csv.
    """
    if input_directory is None:
        input_directory = os.path.join(RAW_DATA_DIR, "unzipped_data")
        
    if not os.path.exists(input_directory):
        # Fallback to searching data/raw directly
        input_directory = RAW_DATA_DIR

    print(f"Scanning for CSV files in: {input_directory}")
    csv_files = glob.glob(os.path.join(input_directory, "**", "*.csv"), recursive=True)
    
    # Exclude the target output file itself if already present
    csv_files = [f for f in csv_files if os.path.abspath(f) != os.path.abspath(OUTPUT_PATH)]

    if not csv_files:
        print(f"Error: No CSV files found in '{input_directory}'.")
        print("Please extract your dataset folder into 'data/raw/unzipped_data/'.")
        return

    print(f"Found {len(csv_files)} CSV files. Merging...")
    
    dataframes = []
    for filepath in csv_files:
        try:
            df = pd.read_csv(filepath)
            
            # If the CSV already has a 'label' or 'class' column, standardize it
            if "label" not in df.columns:
                if "class" in df.columns:
                    df.rename(columns={"class": "label"}, inplace=True)
                elif "Class" in df.columns:
                    df.rename(columns={"Class": "label"}, inplace=True)
                elif "target" in df.columns:
                    df.rename(columns={"target": "label"}, inplace=True)
                else:
                    # Infer label from filename
                    inferred_label = extract_label_from_filename_or_folder(filepath)
                    df["label"] = inferred_label
            
            # Clean string labels
            df["label"] = df["label"].astype(str).str.strip().str.upper()
            dataframes.append(df)
        except Exception as e:
            print(f"Warning: Skipped '{filepath}' due to read error: {e}")

    if not dataframes:
        print("Error: Failed to process any CSV files.")
        return

    # Concatenate all files into one DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Drop completely empty/NaN rows
    combined_df.dropna(how="all", inplace=True)

    # Save to sign_language_data.csv
    combined_df.to_csv(OUTPUT_PATH, index=False)
    
    print("\n==================================================")
    print("           DATASET MERGED SUCCESSFULLY            ")
    print("==================================================")
    print(f"Master CSV Path   : {OUTPUT_PATH}")
    print(f"Total Rows        : {len(combined_df)}")
    print(f"Total Columns     : {len(combined_df.columns)} (including 'label')")
    print(f"Classes Discovered: {sorted(combined_df['label'].unique().tolist())}")
    print("==================================================")

if __name__ == "__main__":
    merge_csv_files()