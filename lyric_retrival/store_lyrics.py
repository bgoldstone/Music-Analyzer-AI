import re
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import time
import json
import dotenv
import os
from pymongo import MongoClient

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"
SONG_DATA_DIRECTORY = "song_data"
SONG_DATA_DIRECTORY_PATH = os.path.join(os.getcwd(), SONG_DATA_DIRECTORY)

# Initialize Spotify and Genius API credentials
spotify_client_id = "5c787e0eccd246ba9c4500f755bff00b"
spotify_client_secret = "a9b2fc8b4eac4f219aaa8dd852e98b1c"
spotify_user_id = "spotify:user:daeshaunmorrison"
spotify_playlist_id = "spotify:playlist:47FWzqz1PwNyKaIApQjF9H" # longer playlist
#spotify_playlist_id ="spotify:playlist:6k6gktoOhlHLrGXr8M8Psy" # shorter playlist
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
    
    def get_track_ids(self):
        track_ids = []
        for song in range(len(self.playlist['items'])):
            track_ids.append(self.playlist['items'][song]['track']['id'])
        self.track_ids = track_ids
        return self.track_ids
        

    def get_lyrics(self):
        playlist = GetLyrics.get_playlist_info(self)
        track_names = GetLyrics.get_track_names(self)
        track_ids = self.get_track_ids()
        track_artists = GetLyrics.get_track_artists(self)
        song_lyrics = {}

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
                # Successful lyric grab
                lyrics_clean = clean_lyrics(song.lyrics)
                
                # Store track information and cleaned lyrics in a nested dictionary
                artist = track_artists[i]
                song_title= track_names[i]
                song_id = track_ids[i]
                lyrics = lyrics_clean

                if(artist not in song_lyrics):
                    song_lyrics[artist] = {song_title : {song_id : lyrics}}
                else:
                    if song_title not in song_lyrics[artist]:
                        song_lyrics[artist][song_title] = {song_id: lyrics}
                    else:
                        song_lyrics[artist][song_title][song_id] = lyrics

        return song_lyrics

# Initialize GetLyrics class with Spotify and Genius credentials
songs = GetLyrics(spotify_client_id, spotify_client_secret, spotify_user_id, spotify_playlist_id, genius_key)
# Retrieve lyrics for all tracks in the playlist
song_lyrics = songs.get_lyrics()

# Write artist-song-lyrics data to a JSON file
#with open("lyric_retrival\\lyrics.json", "w") as json_file:
#    json.dump(song_lyrics, json_file, indent=4)

def get_db_connection() -> MongoClient | None:
    """Creates and returns db connection.

    Returns:
        MongoClient | None: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, ".env"))
    mongo_user = dotenv.dotenv_values().get("MONGO_USER")
    mongo_password = dotenv.dotenv_values().get("MONGO_PASSWORD")
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/"
    client = MongoClient(mongo_uri)
    db = client.soundsmith
    try:
        db.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return
    return db

def load_lyrics(db: MongoClient, id, lyrics):
    track_query = {"track_id": id}

    # Find or create track
    mongo_track = db.lyrics.find_one_and_update(
        track_query,
        {"$set": {"lyrics": lyrics}},
        upsert=True,
        return_document=True,
    )
client = get_db_connection()

for artist, artist_info in song_lyrics.items():
    for song,tuple in artist_info.items():
        for id, lyrics in tuple.items():
            #print(id,lyrics)
            load_lyrics(client, id, lyrics)