# playlist_generator.py
"""
Generate workout playlists using Markov chain state transitions.
"""

import numpy as np
import pandas as pd
from markov_model import compute_bin_centers, build_base_transition, build_phase_matrix, simulate_chain, PHASE_WEIGHTS, STATES
from bpm_binner import choose_song_from_bin

def generate_playlist(df: pd.DataFrame, plan: list, tau: float = 12.0) -> list:
    """
    Generate playlist following a workout plan.
    
    Args:
        df: DataFrame with binned songs
        plan: List of (phase_name, num_songs) tuples
        tau: Temperature parameter for transition matrix
    
    Returns:
        List of song dictionaries
    """
    # Build transition matrices
    centers = compute_bin_centers(df)
    P_base = build_base_transition(centers, tau=tau)
    
    # Create sequence of phase-specific matrices
    P_seq = []
    for phase, length in plan:
        P_phase = build_phase_matrix(P_base, PHASE_WEIGHTS[phase])
        P_seq.extend([P_phase] * length)
    
    # Simulate state path and select songs
    state_path = simulate_chain(P_seq, x0=0)
    used_ids = set()
    playlist = []
    
    for state_idx in state_path[1:]:  # Skip initial state
        state = STATES[state_idx]
        song = choose_song_from_bin(df, state, used_ids)
        
        if song is not None:
            used_ids.add(song["id"])
            playlist.append(song.to_dict())
    
    return playlist

def parse_duration(duration_str):
    """Convert MM:SS string to total seconds."""
    parts = str(duration_str).split(':')
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)
    return 0


def format_duration(total_seconds):
    """Convert total seconds to MM:SS format."""
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def main():
    df = pd.read_csv("songs_binned.csv")
    
    # Workout plan: (phase, number_of_songs)
    plan = [
        ("warmup", 2),
        ("steady_state", 4),
        ("push_pace", 3),
        ("steady_state", 2),
        ("sprint", 1)
    ]
    
    playlist = generate_playlist(df, plan, tau=12.0)
    
    # Calculate total duration
    total_seconds = sum(parse_duration(track['duration']) for track in playlist)
    total_duration_str = format_duration(total_seconds)
    
    print("Generated Playlist:")
    print(f"Total Duration: {total_duration_str}")
    print(f"Number of Songs: {len(playlist)}")
    print()
    print(f"{'State':<15} {'Song':<45} {'BPM':<6} {'Duration'}")
    print("-" * 75)
    
    for track in playlist:
        song_name = track['name'][:42] + "..." if len(track['name']) > 45 else track['name']
        print(f"{track['state']:<15} {song_name:<45} {track['bpm']:<6} {track['duration']}")

if __name__ == "__main__":
    main()