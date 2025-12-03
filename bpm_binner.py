# bpm_binner.py
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional

#load csv
songs = pd.read_csv("songs.csv")

#fixed bin ranges
warmup = (80, 110)
steady_state = (110, 140)
push_pace = (140, 170)
sprint = (170, 1000)

BIN_ORDER = [
    ("warmup", warmup),
    ("steady_state", steady_state),
    ("push_pace", push_pace),
    ("sprint", sprint)
]

def categorize_bpm(bpm):
    for category, (lower, upper) in BIN_ORDER:
        if lower <= bpm < upper:
            return category
    return None

def bin_songs(songs_df: pd.DataFrame, bin_order=BIN_ORDER, id_col: str = "id", bpm_col: str = "bpm") -> Tuple[pd.DataFrame, Dict[str, str]]:
    df_binned = songs_df.copy()
    df_binned["state"] = df_binned['bpm'].apply(categorize_bpm)

    mapping = {str(row["id"]): str(row["state"]) for _, row in df_binned[[id_col, "state"]].iterrows()}

    return df_binned, mapping

if __name__ == "__main__":
    try:
        songs_binned, mapping = bin_songs(songs)
        print(dict(list(mapping.items())[:10]))
    except Exception as e:
        print("Error during binning:", e)
        raise

    for state in ["warmup", "steady_state", "push_pace", "sprint"]:
            # Filter songs in this state
            state_songs = songs_binned[songs_binned["state"] == state]
            count = len(state_songs)
            
            # Get song names
            song_names = state_songs["name"].tolist()
            
            print(f"\n{state.upper().replace('_', ' ')}")
            print(f"Count: {count}")
            print(f"Songs: {', '.join(song_names)}")