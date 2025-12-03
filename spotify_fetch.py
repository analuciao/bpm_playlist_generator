# spotify_fetch.py
"""
Fetch user's Liked Songs and audio features from Spotify.
Saves songs.csv with columns: id,name,artists,duration,bpm,energy,danceability
Requires environment variables:
  SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, RAPIDAPI_KEY
Install: pip install spotipy pandas python-dotenv requests
"""
import os
import time
from typing import List, Dict

import pandas as pd
import requests
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

SCOPE = "user-library-read"
CACHE_PATH = ".cache"


def spotify_auth(scope: str = SCOPE) -> Spotify:
    """Authenticate with Spotify using environment variables."""
    auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=scope,
        cache_path=CACHE_PATH
    )
    return Spotify(auth_manager=auth)


def get_liked_tracks_items(sp: Spotify, max_tracks: int = 50) -> List[Dict]:
    """Fetch liked tracks items from Spotify API."""
    results = sp.current_user_saved_tracks(limit=max_tracks, offset=0)
    return results["items"]


def format_track_string(track: Dict) -> str:
    """Format track as 'Song Name by Artist Name'."""
    return f"{track['name']} by {track['artists'][0]['name']}"


def fetch_liked_tracks(sp: Spotify, max_tracks: int = 50) -> List[str]:
    """Fetch saved tracks (liked songs) as formatted strings."""
    items = get_liked_tracks_items(sp, max_tracks)
    return [format_track_string(item["track"]) for item in items]


def get_audio_features_soundnet(track_id: str, rapid_api_key: str) -> Dict:
    """Fetch audio features from SoundNet API using Spotify track ID."""
    url = f"https://track-analysis.p.rapidapi.com/pktx/spotify/{track_id}"
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "track-analysis.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def fetch_audio_features(sp: Spotify, rapid_api_key: str, max_tracks: int = 50) -> pd.DataFrame:
    """Fetch audio features for all liked tracks and return as DataFrame."""
    items = get_liked_tracks_items(sp, max_tracks)
    rows = []

    for item in items:
        track = item["track"]
        track_id = track["id"]
        
        if not track_id:
            print(f"Skipping track with missing id: {track['name']}")
            continue

        try:
            features = get_audio_features_soundnet(track_id, rapid_api_key)
            
            rows.append({
                "id": track_id,
                "name": track["name"],
                "artists": track["artists"][0]["name"],
                "duration": features.get("duration"),
                "bpm": features.get("tempo"),
                "energy": features.get("energy"),
                "danceability": features.get("danceability")
            })
            
            time.sleep(1.1)  # Rate limiting
    
        except Exception as e:
            print(f"Error fetching features for {track['name']}: {e}")
            continue
        
    return pd.DataFrame(rows)


def main():
    print("Authenticating with Spotify…")
    sp = spotify_auth()
    
    # Fetch and display liked songs
    liked_songs = fetch_liked_tracks(sp, max_tracks=50)
    print("\nYour 50 most recent liked songs:\n")
    for idx, song in enumerate(liked_songs, start=1):
        print(f"{idx:2d}. {song}")
    
    # Fetch audio features and save to CSV
    rapid_api_key = os.getenv("RAPIDAPI_KEY")
    df = fetch_audio_features(sp, rapid_api_key, max_tracks=50)
    
    df.to_csv("songs.csv", index=False)
    print("\nSaved to songs.csv")

if __name__ == "__main__":
    main()

    
