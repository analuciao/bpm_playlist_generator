# evaluate.py
"""Compare playlist generation strategies."""

import pandas as pd
import numpy as np
from playlist_generator import generate_playlist
from markov_model import STATES

def compute_transition_variance(playlist):
    """Measure BPM smoothness (lower = smoother)."""
    bpms = [song['bpm'] for song in playlist]
    transitions = np.diff(bpms)
    return np.var(transitions)

def compute_phase_accuracy(playlist, plan):
    """Check if songs match target phase BPMs."""
    phase_bpms = {"warmup": 95, "steady_state": 125, "push_pace": 155, "sprint": 185}
    
    errors = []
    idx = 0
    for phase, length in plan:
        target_bpm = phase_bpms[phase]
        for i in range(length):
            if idx < len(playlist):
                errors.append(abs(playlist[idx]['bpm'] - target_bpm))
                idx += 1
    
    return np.mean(errors) if errors else 0

def baseline_random(df, plan):
    """Random shuffle baseline."""
    total_songs = sum(length for _, length in plan)
    return df.sample(n=min(total_songs, len(df))).to_dict('records')

def baseline_sorted(df, plan):
    """Sort by BPM baseline."""
    total_songs = sum(length for _, length in plan)
    return df.nsmallest(total_songs, 'bpm').to_dict('records')

def compare_strategies(df, plan):
    """Compare Markov vs baselines."""
    markov_pl = generate_playlist(df, plan)
    random_pl = baseline_random(df, plan)
    sorted_pl = baseline_sorted(df, plan)
    
    results = {
        "Markov": {
            "variance": compute_transition_variance(markov_pl),
            "phase_error": compute_phase_accuracy(markov_pl, plan)
        },
        "Random": {
            "variance": compute_transition_variance(random_pl),
            "phase_error": compute_phase_accuracy(random_pl, plan)
        },
        "Sorted": {
            "variance": compute_transition_variance(sorted_pl),
            "phase_error": compute_phase_accuracy(sorted_pl, plan)
        }
    }
    
    return results

if __name__ == "__main__":
    df = pd.read_csv("songs_binned.csv")
    plan = [("warmup", 2), ("steady_state", 4), ("push_pace", 3), ("sprint", 1)]
    
    results = compare_strategies(df, plan)
    
    print("\nPlaylist Quality Comparison:")
    print(f"{'Strategy':<12} {'BPM Variance':<15} {'Phase Error'}")
    print("-" * 45)
    for strategy, metrics in results.items():
        print(f"{strategy:<12} {metrics['variance']:<15.2f} {metrics['phase_error']:.2f}")