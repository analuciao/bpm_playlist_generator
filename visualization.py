# visualization.py
"""
Visualize BPM distribution of songs.
"""

import pandas as pd
import matplotlib.pyplot as plt

def plot_bpm_histogram(df: pd.DataFrame, output_path: str = "bpm_histogram.png"):
    """Plot and save histogram of song BPMs."""
    bpm = df["bpm"].dropna()
    
    plt.figure(figsize=(8, 5))
    plt.hist(bpm, bins=10, edgecolor="black", alpha=0.75)
    plt.xlabel("BPM", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Distribution of Song BPMs", fontsize=14)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {output_path}")


def main():
    df = pd.read_csv("songs.csv")
    plot_bpm_histogram(df)


if __name__ == "__main__":
    main()