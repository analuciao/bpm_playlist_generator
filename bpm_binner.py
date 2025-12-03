# bpm_binner.py
import pandas as pd

# BPM ranges for workout states
BINS = {
    "warmup": (80, 110),
    "steady_state": (110, 140),
    "push_pace": (140, 170),
    "sprint": (170, 1000)
}

def categorize_bpm(bpm: float) -> str:
    """Assign a workout state based on BPM."""
    for state, (lower, upper) in BINS.items():
        if lower <= bpm < upper:
            return state
    return None

def bin_songs(songs_df: pd.DataFrame) -> pd.DataFrame:
    """Add 'state' column to songs based on BPM."""
    df = songs_df.copy()
    df["state"] = df["bpm"].apply(categorize_bpm)
    return df


def choose_song_from_bin(songs_df: pd.DataFrame, state: str, used_ids: set):
    """Select a random unused song from the given state, or fallback to any unused song."""
    unused = songs_df[~songs_df["id"].isin(used_ids)]
    
    # Try to find song in requested state
    candidates = unused[unused["state"] == state]
    if not candidates.empty:
        return candidates.sample(1).iloc[0]
    
    # Fallback to any unused song
    if not unused.empty:
        return unused.sample(1).iloc[0]
    
    return None


def main():
    songs = pd.read_csv("songs.csv")
    songs_binned = bin_songs(songs)
    
    # Print summary by state
    for state in BINS.keys():
        state_songs = songs_binned[songs_binned["state"] == state]
        song_names = state_songs["name"].tolist()
        
        print(f"\n{state.upper().replace('_', ' ')}")
        print(f"Count: {len(state_songs)}")
        print(f"Songs: {', '.join(song_names)}")
    
    songs_binned.to_csv("songs_binned.csv", index=False)

if __name__ == "__main__":
    main()