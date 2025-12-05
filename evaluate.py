# evaluate.py
"""
Compare playlist generation strategies and compute Markov chain properties.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from playlist_generator import generate_playlist, STATES, PHASE_WEIGHTS
from bpm_binner import BINS
from markov_model import compute_bin_centers, build_base_transition


def compute_transition_variance(playlist):
    """Measure BPM smoothness (lower = smoother transitions)."""
    bpms = [song['bpm'] for song in playlist]
    transitions = np.diff(bpms)
    return float(np.var(transitions))

def compute_phase_accuracy(playlist, plan):
    """Check how well songs match target phase BPMs."""
    # Use bin midpoints as targets (handle sprint bin specially)
    phase_bpms = {
        "warmup": sum(BINS["warmup"]) / 2,
        "steady_state": sum(BINS["steady_state"]) / 2,
        "push_pace": sum(BINS["push_pace"]) / 2,
        "sprint": 180  # Use realistic upper bound instead of midpoint of (170, 1000)
    }
    
    errors = []
    idx = 0
    for phase, length in plan:
        target_bpm = phase_bpms[phase]
        for _ in range(length):
            if idx < len(playlist):
                errors.append(abs(playlist[idx]['bpm'] - target_bpm))
                idx += 1
    
    return float(np.mean(errors)) if errors else 0.0

def compute_expected_hitting_times(P, target_state_idx):
    """
    Compute expected hitting time to target state from all other states.
    
    Solves the linear system:
        h(i) = 1 + sum_j P_ij * h(j)  for i != target
        h(target) = 0
    
    Returns: array of expected hitting times for each state
    """
    n = P.shape[0]
    
    # Set up linear system (I - P) h = 1, excluding target state
    # solve: h(i) - sum_j P_ij h(j) = 1
    non_target = [i for i in range(n) if i != target_state_idx]
    
    # Extract submatrix excluding target state
    P_sub = P[np.ix_(non_target, non_target)]
    I_sub = np.eye(len(non_target))
    
    # Solve (I - P_sub) h_sub = 1
    A = I_sub - P_sub
    b = np.ones(len(non_target))
    
    try:
        h_sub = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        # Fallback for singular matrix
        h_sub = np.linalg.lstsq(A, b, rcond=None)[0]
    
    # Reconstruct full hitting time vector
    h = np.zeros(n)
    for i, state_idx in enumerate(non_target):
        h[state_idx] = h_sub[i]
    
    return h


def baseline_random(df, plan):
    """Random shuffle baseline."""
    total_songs = sum(length for _, length in plan)
    sampled = df.sample(n=min(total_songs, len(df)))
    return sampled.to_dict('records')


def baseline_sorted(df, plan):
    """Sort by BPM baseline (ascending)."""
    total_songs = sum(length for _, length in plan)
    sorted_df = df.nsmallest(total_songs, 'bpm')
    return sorted_df.to_dict('records')


def compare_strategies(df, plan, n_trials=5):
    """
    Compare Markov vs baselines over multiple trials.
    Returns mean and std of metrics.
    """
    results = {
        "Markov": {"variance": [], "phase_error": []},
        "Random": {"variance": [], "phase_error": []},
        "Sorted": {"variance": [], "phase_error": []}
    }
    
    for trial in range(n_trials):
        # Generate playlists
        markov_pl = generate_playlist(df, plan)
        random_pl = baseline_random(df, plan)
        sorted_pl = baseline_sorted(df, plan)
        
        # Compute metrics
        results["Markov"]["variance"].append(compute_transition_variance(markov_pl))
        results["Markov"]["phase_error"].append(compute_phase_accuracy(markov_pl, plan))
        
        results["Random"]["variance"].append(compute_transition_variance(random_pl))
        results["Random"]["phase_error"].append(compute_phase_accuracy(random_pl, plan))
        
        results["Sorted"]["variance"].append(compute_transition_variance(sorted_pl))
        results["Sorted"]["phase_error"].append(compute_phase_accuracy(sorted_pl, plan))
    
    # Compute means and stds
    summary = {}
    for strategy in results:
        summary[strategy] = {
            "variance_mean": np.mean(results[strategy]["variance"]),
            "variance_std": np.std(results[strategy]["variance"]),
            "phase_error_mean": np.mean(results[strategy]["phase_error"]),
            "phase_error_std": np.std(results[strategy]["phase_error"])
        }
    
    return summary


def analyze_sensitivity(df, tau_values=[5.0, 10.0, 15.0, 20.0]):
    """
    Analyze how tau affects transition smoothness and hitting times.
    """
    plan = [("warmup", 2), ("steady_state", 3), ("push_pace", 2), ("sprint", 1)]
    
    results = []
    for tau in tau_values:
        # Generate playlist with this tau
        playlist = generate_playlist(df, plan, tau=tau)
        variance = compute_transition_variance(playlist)
        
        # Compute hitting time to sprint state
        centers = compute_bin_centers(df)
        P = build_base_transition(centers, tau=tau)
        sprint_idx = STATES.index("sprint")
        hitting_times = compute_expected_hitting_times(P, sprint_idx)
        warmup_to_sprint = hitting_times[0]  # From warmup state
        
        results.append({
            "tau": tau,
            "variance": variance,
            "hitting_time": warmup_to_sprint
        })
    
    return pd.DataFrame(results)


def plot_sensitivity_analysis(sensitivity_df, output_path="sensitivity_analysis.png"):
    """Plot tau vs variance and hitting time."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot variance
    ax1.plot(sensitivity_df["tau"], sensitivity_df["variance"], 'o-', linewidth=2, markersize=8)
    ax1.set_xlabel("τ (temperature)", fontsize=12)
    ax1.set_ylabel("BPM Transition Variance", fontsize=12)
    ax1.set_title("Smoothness vs Temperature", fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # Plot hitting time
    ax2.plot(sensitivity_df["tau"], sensitivity_df["hitting_time"], 'o-', 
             linewidth=2, markersize=8, color='#C73E1D')
    ax2.set_xlabel("τ (temperature)", fontsize=12)
    ax2.set_ylabel("Expected Steps to Sprint", fontsize=12)
    ax2.set_title("Hitting Time vs Temperature", fontsize=13)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_path}")


def main():
    df = pd.read_csv("songs_binned.csv")
    
    # Standard workout plan
    plan = [
        ("warmup", 2),
        ("steady_state", 4),
        ("push_pace", 3),
        ("steady_state", 2),
        ("sprint", 1)
    ]
    
    print("=" * 60)
    print("PLAYLIST STRATEGY COMPARISON")
    print("=" * 60)
    
    # Compare strategies
    comparison = compare_strategies(df, plan, n_trials=10)
    
    print(f"\n{'Strategy':<12} {'BPM Variance':<20} {'Phase Error (BPM)'}")
    print("-" * 60)
    for strategy, metrics in comparison.items():
        var_str = f"{metrics['variance_mean']:.1f} ± {metrics['variance_std']:.1f}"
        err_str = f"{metrics['phase_error_mean']:.1f} ± {metrics['phase_error_std']:.1f}"
        print(f"{strategy:<12} {var_str:<20} {err_str}")
    
    # Compute expected hitting times for base transition matrix
    print("\n" + "=" * 60)
    print("EXPECTED HITTING TIMES TO SPRINT STATE")
    print("=" * 60)
    
    centers = compute_bin_centers(df)
    P_base = build_base_transition(centers, tau=12.0)
    sprint_idx = STATES.index("sprint")
    hitting_times = compute_expected_hitting_times(P_base, sprint_idx)
    
    print("\nExpected number of steps to reach Sprint from:")
    for i, state in enumerate(STATES):
        if i != sprint_idx:
            print(f"  {state:<15}: {hitting_times[i]:.2f} steps")
    
    # Sensitivity analysis
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS (τ parameter)")
    print("=" * 60)
    
    sensitivity_df = analyze_sensitivity(df)
    print("\n", sensitivity_df.to_string(index=False))
    
    plot_sensitivity_analysis(sensitivity_df)
    
    print("\n" + "=" * 60)
    print("Analysis complete! Check sensitivity_analysis.png")
    print("=" * 60)


if __name__ == "__main__":
    main()