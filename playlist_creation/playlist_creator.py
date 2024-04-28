import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pymongo import MongoClient
import dotenv
import os
import random

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

client_id = '5c787e0eccd246ba9c4500f755bff00b'
client_secret = 'a9b2fc8b4eac4f219aaa8dd852e98b1c'
redirect_uri = 'http://localhost:8000/oauth/spotify'

# PLEASE DONT RUN THIS TOO OFTEN AS IT CREATES A PLAYLIST IN MY (TREVOR'S) SPOTIFY ACCOUNT

# Initialize Spotipy with necessary credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= client_id,
                                               client_secret= client_secret,
                                               redirect_uri= redirect_uri,
                                               scope='playlist-modify-public'))

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

def create_playlist(name, description):
    # Create the playlist
    playlist = sp.user_playlist_create(sp.me()['id'], name, public=True, description=description)
    return playlist['id']

def add_songs_to_playlist(playlist_id, db):

    song_ids = []

    # Grab songs from DB to populate song_ids
    db_tracks = list(db.tracks.find({}))

    for _ in range(5):
        rand_track_id = random.randrange(0,len(db_tracks))
        print(db_tracks[rand_track_id]['track_name'])
        song_ids.append(db_tracks[rand_track_id]['spotify']['track_id'])
    
    # Add songs to the playlist
    sp.playlist_add_items(playlist_id, song_ids)

def main():
    db = get_db_connection()

    # Create a new playlist
    playlist_id = create_playlist('SongSmith playlist', 'A playlist created using Python')

    # Add songs to the playlist
    add_songs_to_playlist(playlist_id, db)

    print("Playlist created successfully!")

if __name__ == "__main__":
    main()
