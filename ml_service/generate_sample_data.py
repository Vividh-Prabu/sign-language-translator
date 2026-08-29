"""
generate_sample_data.py
------------------------
Creates a SIMULATED sign-language glove dataset so we can build and test the
whole ML pipeline before real hardware data exists. Each gesture gets its own
sensor "center" plus random noise, and we deliberately inject a little mess
(missing values, duplicates, impossible readings) for the cleaning phase.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

labels = ["A", "B", "C", "D", "E", "SPACE", "DELETE"]
SAMPLES_PER_LABEL = 150

feature_names = [
    "flex1", "flex2", "flex3", "flex4", "flex5",
    "acc_x", "acc_y", "acc_z",
    "gyro_x", "gyro_y", "gyro_z",
    "temperature",
]

rows = []
for label in labels:
    flex_center = rng.uniform(300, 700, size=5)
    acc_center = rng.uniform(-1.0, 1.0, size=3)
    gyro_center = rng.uniform(-30, 30, size=3)
    for _ in range(SAMPLES_PER_LABEL):
        flex = flex_center + rng.normal(0, 25, size=5)
        acc = acc_center + rng.normal(0, 0.15, size=3)
        gyro = gyro_center + rng.normal(0, 5, size=3)
        temperature = rng.normal(31.0, 0.3)
        row = list(flex) + list(acc) + list(gyro) + [temperature, label]
        rows.append(row)

df = pd.DataFrame(rows, columns=feature_names + ["label"])
df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

# Deliberate messiness for the preprocessing phase:
for _ in range(15):                                  # 1) missing values
    r = int(rng.integers(0, len(df)))
    c = int(rng.integers(0, len(feature_names)))
    df.iat[r, c] = np.nan

duplicates = df.sample(5, random_state=RANDOM_SEED)  # 2) duplicate rows
df = pd.concat([df, duplicates], ignore_index=True)

df.iat[int(rng.integers(0, len(df))), 0] = -999      # 3) impossible values
df.iat[int(rng.integers(0, len(df))), 1] = 5000

for col in feature_names:
    df[col] = df[col].round(2)

out_path = Path("data/raw/sign_language_data.csv")
out_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out_path, index=False)

print(f"Wrote {len(df)} rows to {out_path}")
print("\nSamples per label:")
print(df["label"].value_counts())