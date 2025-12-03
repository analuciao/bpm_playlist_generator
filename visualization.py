# visualization.py
"""
Visualize BPM distribution of songs.
"""

import pandas as pd
import matplotlib.pyplot as plt
from playlist_generator import generate_playlist

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


def plot_playlist_timeline(playlist, plan, output_path="playlist_timeline.png"):
    """Plot BPM over time with workout phases highlighted."""
    import matplotlib.patches as mpatches
    
    bpms = [song['bpm'] for song in playlist]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot BPM line
    ax.plot(range(len(bpms)), bpms, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    
    # Shade background by phase
    colors = {"warmup": "#A23B72", "steady_state": "#F18F01", 
              "push_pace": "#C73E1D", "sprint": "#6A0572"}
    
    idx = 0
    for phase, length in plan:
        ax.axvspan(idx, idx + length, alpha=0.2, color=colors.get(phase, 'gray'))
        idx += length
    
    ax.set_xlabel("Song Number", fontsize=12)
    ax.set_ylabel("BPM", fontsize=12)
    ax.set_title("Generated Playlist BPM Timeline", fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    
    # Legend
    patches = [mpatches.Patch(color=colors[p], alpha=0.3, label=p.replace('_', ' ').title()) 
               for p, _ in plan]
    ax.legend(handles=patches, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_path}")


def main():
    df_binned = pd.read_csv("songs_binned.csv")
    df = pd.read_csv("songs.csv")

    plan = [
        ("warmup", 2),
        ("steady_state", 4),
        ("push_pace", 3),
        ("steady_state", 2),
        ("sprint", 1)
    ]

    playlist = generate_playlist(df_binned, plan, tau=12.0)

    plot_playlist_timeline(playlist, plan)
    plot_bpm_histogram(df)
    

if __name__ == "__main__":
    main()