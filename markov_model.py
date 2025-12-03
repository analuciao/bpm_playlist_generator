# markov_model.py
"""
Build Markov transition matrices from BPM-binned songs.
Expects songs_binned.csv with columns: id, bpm, state
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Workout states in order
STATES = ["warmup", "steady_state", "push_pace", "sprint"]

# Phase-specific transition weights
PHASE_WEIGHTS = {
    "warmup": [2.0, 1.2, 0.8, 0.5],
    "steady_state": [1.0, 2.0, 1.0, 0.8],
    "push_pace": [0.7, 1.0, 2.0, 1.0],
    "sprint": [0.5, 0.8, 1.0, 2.5],
}


def compute_bin_centers(df: pd.DataFrame) -> np.ndarray:
    """Compute mean BPM for each state."""
    centers = [df[df["state"] == state]["bpm"].mean() for state in STATES]
    return np.array(centers, dtype=float)


def build_similarity_matrix(centers: np.ndarray, tau: float = 12.0) -> np.ndarray:
    """Build similarity matrix using Laplace kernel: exp(-|d|/tau)."""
    n = len(centers)
    distances = np.abs(centers[:, None] - centers[None, :])
    return np.exp(-distances / tau)


def row_normalize(mat: np.ndarray) -> np.ndarray:
    """Row-normalize matrix so each row sums to 1."""
    row_sums = mat.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0  # Avoid division by zero
    return mat / row_sums


def build_base_transition(centers: np.ndarray, tau: float = 12.0) -> np.ndarray:
    """Build base transition matrix from BPM centers."""
    S = build_similarity_matrix(centers, tau)
    return row_normalize(S)


def build_phase_matrix(P_base: np.ndarray, weights: list) -> np.ndarray:
    """Apply phase-specific weights to base transition matrix."""
    weighted = P_base * np.array(weights)
    return row_normalize(weighted)


def simulate_chain(P_seq: list, x0: int = 0) -> list:
    """
    Simulate time-inhomogeneous Markov chain.
    P_seq: list of transition matrices
    x0: starting state index
    Returns: list of visited states
    """
    state = x0
    path = [state]
    
    for P in P_seq:
        state = np.random.choice(len(P), p=P[state])
        path.append(state)
    
    return path


def save_matrix_json(mat: np.ndarray, path: str):
    """Save matrix as JSON with state labels."""
    obj = {
        "labels": STATES,
        "matrix": np.round(mat, 4).tolist()
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def plot_heatmap(mat: np.ndarray, path: str, title: str):
    """Plot and save transition matrix heatmap."""
    plt.figure(figsize=(6, 5))
    plt.imshow(mat, cmap="viridis", aspect="auto", interpolation="nearest")
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.xticks(range(len(STATES)), STATES, rotation=45, ha="right")
    plt.yticks(range(len(STATES)), STATES)
    plt.title(title)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    # Load binned songs
    df = pd.read_csv("songs_binned.csv")
    
    # Compute BPM centers for each state
    centers = compute_bin_centers(df)
    print("State BPM centers:")
    for state, center in zip(STATES, centers):
        print(f"  {state}: {center:.1f}")
    
    # Build base transition matrix
    P_base = build_base_transition(centers, tau=12.0)
    print("\nBase transition matrix:")
    print(pd.DataFrame(np.round(P_base, 3), index=STATES, columns=STATES))
    
    # Save base matrix
    os.makedirs("matrices", exist_ok=True)
    save_matrix_json(P_base, "matrices/P_base.json")
    plot_heatmap(P_base, "matrices/P_base.png", "Base Transition Matrix")
    
    # Build and save phase-specific matrices
    for phase, weights in PHASE_WEIGHTS.items():
        P_phase = build_phase_matrix(P_base, weights)
        print(f"\nP_{phase}:")
        print(pd.DataFrame(np.round(P_phase, 3), index=STATES, columns=STATES))
        
        save_matrix_json(P_phase, f"matrices/P_{phase}.json")
        plot_heatmap(P_phase, f"matrices/P_{phase}.png", f"P_{phase}")
    
    print("\nMatrices saved to matrices/")


if __name__ == "__main__":
    main()