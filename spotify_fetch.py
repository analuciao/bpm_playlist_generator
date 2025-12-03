# spotify_fetch.py
"""
Fetch user's Liked Songs and audio features from Spotify.
Saves songs.csv with columns: id,name,artists,duration_ms,bpm,energy,danceability
Requires environment variables:
  SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
Install: pip install spotipy pandas
"""
from dotenv import load_dotenv
load_dotenv()

import os, time
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict
import requests

SCOPE = "user-library-read"
CACHE_PATH = ".cache"
rapidapi_key = os.getenv("RAPIDAPI_KEY")

def spotify_auth(client_id=None, client_secret=None, redirect_uri=None, scope=SCOPE) -> Spotify:
    # uses env vars if None
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    auth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, cache_path=CACHE_PATH)
    sp = Spotify(auth_manager=auth)
    return sp


def fetch_liked_tracks(sp: Spotify, max_tracks: int = 50) -> List[Dict]:
    """Fetch saved tracks (liked songs). Returns list of track dicts from API responses."""
    results = sp.current_user_saved_tracks(limit=max_tracks, offset=0)
    items = results["items"]
    tracks = []
    
    for item in items:
        track = item["track"]
        song_name = track["name"]
        artist_name = track['artists'][0]['name']
        tracks.append(f"{song_name} by {artist_name}")
        
    return tracks

def get_audio_features_soundnet(track_id: str, rapid_api_key: str):
    """Fetch audio features from SoundNet API using Spotify track ID"""
    url = f"https://track-analysis.p.rapidapi.com/pktx/spotify/{track_id}"

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "track-analysis.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if request fails
    return response.json()


def fetch_audio_features(sp: Spotify, rapidapi_key: str, max_tracks: int = 50) -> pd.DataFrame:
    results = sp.current_user_saved_tracks(limit=max_tracks, offset=0)
    items = results["items"]

    rows = []

    for item in items:
        track = item["track"]
        tid = track["id"]
        song_name = track["name"]
        artist_name = track["artists"][0]["name"]

        if not tid:
            print(f"Skipping track with missing id: {song_name}")
            continue

        try:
            features = get_audio_features_soundnet(tid, rapidapi_key)

            rows.append({
                "id": tid,
                "name": song_name,
                "artists": artist_name,
                "duration": features.get("duration"),
                "bpm": features.get("tempo"),
                "energy": features.get("energy"),
                "danceability": features.get("danceability")
            })

            time.sleep(1.1)
    
        except Exception as e:
            print(f"Error fetching features for {song_name}: {e}")
            continue
        
    return pd.DataFrame(rows)

        

def main():
    print("Authenticating with Spotify…")
    sp = spotify_auth()
    likedSongs = fetch_liked_tracks(sp, max_tracks = 50) 

    print(likedSongs[0])
    print("\nYour 50 most recent liked songs:\n")
    for idx, song in enumerate(likedSongs, start=1):
        print(f"{idx:2d}. {song}")
    
    df = fetch_audio_features(sp, rapidapi_key, max_tracks=50)
    print("\nDataFrame preview:")
    print(df.head(10).to_string(index=False))
    df.to_csv("songs.csv", index=False)


if __name__ == "__main__":
    main()

    
