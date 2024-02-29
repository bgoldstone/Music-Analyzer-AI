import dotenv
from pymongo import MongoClient
import os
import json
from datetime import datetime

MONGO_URL = 'soundsmith.x5y65kb.mongodb.net'
SONG_DATA_DIRECTORY = 'song_data'
SONG_DATA_DIRECTORY_PATH = os.path.join(os.getcwd(), SONG_DATA_DIRECTORY)


def main():
    client = get_db_connection()
    load_playlists(client)


def get_db_connection() -> MongoClient | None:
    """Creates and returns db connection.
    Returns:
        MongoClient | None: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, '.env'))
    mongo_user = dotenv.dotenv_values().get('MONGO_USER')
    mongo_password = dotenv.dotenv_values().get('MONGO_PASSWORD')
    mongo_uri = f'mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/'
    client = MongoClient(mongo_uri)
    db = client.soundsmith
    try:
        db.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return
    return db


def load_playlists(db: MongoClient) -> None:
    # for each user
    for folders in os.listdir(SONG_DATA_DIRECTORY_PATH):
        user_query = {'username': folders}
        user = db['users'].find_one(user_query)
        if user is None:
            user_query['time'] = datetime.now()
            user = db['users'].insert_one(
                user_query).inserted_id

        # For each playlist
        for files in os.listdir(os.path.join(SONG_DATA_DIRECTORY_PATH, folders)):
            if not files.endswith("_track_details.json"):
                continue
            playlist_name = files.replace('_track_details.json', '')
            songs = []
            with open(os.path.join(SONG_DATA_DIRECTORY_PATH, folders, files), 'r') as f:
                songs = json.load(
                    open(os.path.join(SONG_DATA_DIRECTORY_PATH, folders, files)))
            # For each track
            playlist_query = {'playlist_name': playlist_name, 'user_id': user}
            song_ids = []
            for song in songs:
                track = db.tracks.find_one({'track_id': song['track_id']})
                if (track is not None):
                    song_ids.append(track.get('_id'))
                    continue
                song_id = db.tracks.insert_one(song).inserted_id
                song_ids.append(song_id)
            db.playlists.update_one(
                playlist_query, {'$set': {'songs': songs, "time": datetime.now()}}, upsert=True
            )


if __name__ == '__main__':
    main()
