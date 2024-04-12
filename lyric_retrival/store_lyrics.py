import re
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import time
import json

# Initialize Spotify and Genius API credentials
spotify_client_id = "5c787e0eccd246ba9c4500f755bff00b"
spotify_client_secret = "a9b2fc8b4eac4f219aaa8dd852e98b1c"
spotify_user_id = "spotify:user:daeshaunmorrison"
spotify_playlist_id = "spotify:playlist:47FWzqz1PwNyKaIApQjF9H"
spotify_playlist_id ="spotify:playlist:6k6gktoOhlHLrGXr8M8Psy"
genius_key = "dZCHAObV2X7ZCH4QN2bewuX7lAVoVHedaot3cNn8l_dpwtSwWEaK1cHg8TrbhDtq"
genius_token='4Os3tEbxKSqR_gE76OqwUY3TTQVO11MVLDy14ZmmrC4AS0SygKak8dpgZy3wb5pe'
genius = lyricsgenius.Genius(genius_token)

def clean_lyrics(txt):
    no_brackets = re.sub(r'\[.*?\]', '', txt)
    no_artist = re.sub(r'^(.*?\n)','',no_brackets)
    return no_artist

class GetLyrics():
    
    def __init__(self, spotify_client_id, spotify_client_secret, user_id, playlist_id, genius_key):
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.genius_key = genius_key
        
    def get_playlist_info(self):
        token = SpotifyClientCredentials(client_id=self.spotify_client_id, client_secret=self.spotify_client_secret)
        sp = spotipy.Spotify(client_credentials_manager=token)
        playlist = sp.user_playlist_tracks(self.user_id, self.playlist_id)
        self.playlist = playlist
        return self.playlist
    
    def get_track_names(self):
        track_names = []
        for song in range(len(self.playlist['items'])):
            track_names.append(self.playlist['items'][song]['track']['name'])
        self.track_names = track_names
        return self.track_names
    
    def get_track_artists(self):
        track_artists = []
        for song in range(len(self.playlist['items'])):
            track_artists.append(self.playlist['items'][song]['track']['artists'][0]['name'])
        self.track_artists = track_artists
        return self.track_artists
        
    def get_lyrics(self):
        playlist = GetLyrics.get_playlist_info(self)
        track_names = GetLyrics.get_track_names(self)
        track_artists = GetLyrics.get_track_artists(self)
        song_lyrics_dict = {}

        MAX_SONGS = 1000

        for i in range(len(track_names)):
            # the delay for each API call. Initialized to 3 and increase if there's a time out.
            delay = 3

            time.sleep(delay)
            print("\n")
            print(f"Working on track {i}: {track_names[i]} {track_artists[i]}.")
            
            attempt = 0
            max_attempts = 3  # Maximum number of attempts for each song
            
            while attempt <= max_attempts:
                try:
                    song = genius.search_song(track_names[i], artist=track_artists[i])
                    if song is not None and song.lyrics is not None:
                        break  # If song is found and lyrics are available, exit the loop
                except Exception as e:
                    print(f"Error occurred: {e}")
                    print("Retrying...")
                    delay *= 3
                    time.sleep(delay)
                finally:
                    attempt += 1
            
            if song is None or song.lyrics is None:
                print(f"Track {i} is not in the Genius database.")
            else:
                # Store track information and cleaned lyrics in a nested dictionary
                artist = track_artists[i],
                song= track_names[i],
                lyrics = clean_lyrics(song.lyrics)
                if(artist not in song_lyrics_dict):
                    song_lyrics_dict[artist] = {song : lyrics}
                else:
                    song_lyrics_dict[artist][song] = lyrics

        return song_lyrics_dict


# Initialize GetLyrics class with Spotify and Genius credentials
songs = GetLyrics(spotify_client_id, spotify_client_secret, spotify_user_id, spotify_playlist_id, genius_key)
# Retrieve lyrics for all tracks in the playlist
song_lyrics = songs.get_lyrics()

# Write artist-song-lyrics data to a JSON file
with open("lyric_retrival\\lyrics.json", "w") as json_file:
    json.dump(song_lyrics, json_file, indent=4)