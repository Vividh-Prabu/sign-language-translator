"""
visualize_data.py
-----------------
Creates and saves visualizations to understand the dataset BEFORE cleaning:
class balance, feature distributions, outlier boxplots, correlation heatmap.
Reuses load_dataset() so the raw file is never modified.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from load_data import load_dataset   # reuse our read-only loader

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")


def plot_class_balance(df):
    """Bar chart: how many samples per gesture."""
    plt.figure(figsize=(8, 5))
    order = sorted(df["label"].unique())
    sns.countplot(data=df, x="label", order=order, color="steelblue")
    plt.title("Samples per gesture (class balance)")
    plt.xlabel("Gesture")
    plt.ylabel("Number of samples")
    plt.tight_layout()
    out = FIGURES_DIR / "class_balance.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved {out}")


def plot_feature_distributions(df):
    """Histogram of every feature — shows spread and weird values."""
    feature_cols = [c for c in df.columns if c != "label"]
    df[feature_cols].hist(figsize=(14, 10), bins=30)
    plt.suptitle("Distribution of each feature")
    plt.tight_layout()
    out = FIGURES_DIR / "feature_distributions.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved {out}")


def plot_flex_boxplots(df):
    """Boxplots of flex sensors — outliers show up as far-away dots."""
    flex_cols = [c for c in df.columns if c.startswith("flex")]
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df[flex_cols])
    plt.title("Flex sensor boxplots (spot the impossible values)")
    plt.ylabel("Sensor value")
    plt.tight_layout()
    out = FIGURES_DIR / "flex_boxplots.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved {out}")


def plot_correlation_heatmap(df):
    """Heatmap of feature-to-feature correlation — reveals redundancy."""
    feature_cols = [c for c in df.columns if c != "label"]
    corr = df[feature_cols].corr()
    plt.figure(figsize=(11, 9))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                square=True, cbar_kws={"shrink": 0.8})
    plt.title("Feature correlation heatmap")
    plt.tight_layout()
    out = FIGURES_DIR / "correlation_heatmap.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    df = load_dataset()
    plot_class_balance(df)
    plot_feature_distributions(df)
    plot_flex_boxplots(df)
    plot_correlation_heatmap(df)
    print("\nAll figures saved in the 'figures/' folder.")