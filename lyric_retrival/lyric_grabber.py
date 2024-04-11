import requests
import time
import json
from azlyrics.azlyrics import lyrics
import re

def clean_artist(input_string):
    # Define the regular expression pattern
    pattern = r'^the (.*)$'
    
    # Use re.sub() to remove "the" if it occurs at the beginning of the string
    result = re.sub(pattern, r'\1', input_string)
    return result

# Last.fm API base URL
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Last.fm API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = "7521955e311c356bc257fa614da02c1e"

# Parameters for the artist search
params = {
    "method": "chart.gettopartists",
    "api_key": API_KEY,
    "format": "json",
    "limit": 3
}

# Make a request to the Last.fm API to get top artists
response = requests.get(BASE_URL, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    artists = data["artists"]["artist"]

    # List to store artist-song-lyrics dictionaries
    artist_song_lyrics = []

    # Iterate over each artist to fetch their top tracks
    for artist in artists:
        time.sleep(1)
        artist_name = artist["name"]

        # Parameters for fetching top tracks for the current artist
        params = {
            "method": "artist.gettoptracks",
            "artist": artist_name,
            "api_key": API_KEY,
            "format": "json",
            "limit": 5
        }

        # Make a request to the Last.fm API to get top tracks for the artist
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            # Extract the list of top tracks
            top_tracks = data["toptracks"]["track"]
            # Iterate over top tracks to fetch lyrics
            for track in top_tracks:
                song_name = track["name"]
                artist_clean = clean_artist(artist_name.lower())
                # Fetch lyrics for the song
                song_lyrics = lyrics(artist_clean, song_name)

                if(type(song_lyrics)==list):
                    #print((song_lyrics))
                    song_lyrics = song_lyrics[0]

                if song_lyrics:
                    # Store artist, song, and lyrics in a dictionary
                    artist_song_lyrics.append({
                        "artist": artist_clean,
                        "song": song_name,
                        "lyrics": song_lyrics
                    })
                else:
                    print(f"Failed to fetch lyrics for '{song_name}' by '{artist_clean}'")
        else:
            print(f"Failed to retrieve top tracks for {artist_name}")

    # Write artist-song-lyrics data to a JSON file
    with open("lyric_retrival\\lyrics.json", "w") as json_file:
        json.dump(artist_song_lyrics, json_file, indent=4)
    

    print("Data written to lyrics.json")
else:
    print("Failed to retrieve data from the Last.fm API")
