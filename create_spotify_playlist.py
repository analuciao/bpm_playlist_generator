# create_spotify_playlist.py
"""
Generate a workout playlist and create it in Spotify.
"""

import os
from dotenv import load_dotenv
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from playlist_generator import generate_playlist
from workout_templates import WORKOUTS

load_dotenv()

SCOPE = "user-library-read playlist-modify-public playlist-modify-private"

plan = WORKOUTS["default"]
tau: float=12.0

def spotify_auth():
    """Authenticate with Spotify (with playlist creation scope)."""
    auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=SCOPE,
        cache_path=".cache-create-playlist" 
    )
    return Spotify(auth_manager=auth)

def create_spotify_playlist(sp, playlist_name, description, track_ids):
    user_id = sp.current_user()["id"]

    playlist = sp.user_playlist_create(user_id, playlist_name, False, False, description)   
    sp.user_playlist_add_tracks(user_id, playlist["id"], track_ids)
    return playlist["external_urls"]["spotify"]

def main():
    print("BPM-Adaptive Workout Playlist Generator")
    print("=" * 50)
    
    # Load binned songs
    df = pd.read_csv("songs_binned.csv")
    
    # Generate playlist
    print("\nGenerating playlist...")
    playlist = generate_playlist(df, plan, tau=12.0)
    
    # Display generated playlist
    print(f"\Generated {len(playlist)} songs:")
    for i, track in enumerate(playlist, 1):
        print(f"  {i:2d}. {track['name'][:40]:40s} - {track['state']:12s} ({track['bpm']} BPM)")
    
    # Get playlist name from user
    playlist_name = input("\nEnter playlist name (or press Enter for default): ").strip()
    if not playlist_name:
        playlist_name = "Markov Workout Mix"
    
    # Create description
    phase_summary = ", ".join([f"{length} {phase.replace('_', ' ')}" for phase, length in plan])
    description = f"BPM-adaptive workout: {phase_summary}. Generated using Markov chains."
    
    # Authenticate and create playlist
    print("\nAuthenticating with Spotify...")
    sp = spotify_auth()
    
    print("Creating playlist in Spotify...")
    track_ids = [track['id'] for track in playlist]
    playlist_url = create_spotify_playlist(sp, playlist_name, description, track_ids)
    
    print(f"\nPlaylist created:")
    print(f"   {playlist_url}")
    print("\n   Open Spotify to listen!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
