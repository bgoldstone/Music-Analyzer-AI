import dotenv
from datetime import datetime
import json
import os
from pymongo import MongoClient

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"
SONG_DATA_DIRECTORY = "song_data"
SONG_DATA_DIRECTORY_PATH = os.path.join(os.getcwd(), SONG_DATA_DIRECTORY)


def main():
    client = get_db_connection()
    load_playlists(client)


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


def load_playlists(db: MongoClient) -> None:
    # for each user
    for user_folder in os.listdir(SONG_DATA_DIRECTORY_PATH):
        if(not os.path.isdir(os.path.join(SONG_DATA_DIRECTORY_PATH, user_folder))):
            continue
        user_query = {"username": user_folder}
        # Find or create user
        mongo_user = db["users"].find_one_and_update(
            user_query,
            {"$set": {"username": user_folder, "time": datetime.now()}},
            upsert=True,
            return_document=True,
        )

        # For each playlist
        for playlist_file in os.listdir(
            os.path.join(SONG_DATA_DIRECTORY_PATH, user_folder)
        ):
            # if not track_details file, skip it.
            if not playlist_file.endswith("_track_details.json"):
                continue
            # Get playlist name
            playlist_name = playlist_file.replace("_track_details.json", "")
            # Get tracks
            with open(
                os.path.join(SONG_DATA_DIRECTORY_PATH, user_folder, playlist_file), "r"
            ) as f:
                tracks = json.load(f)
            playlist_query = {
                "playlist_name": playlist_name,
                "user_id": mongo_user.get("_id"),
            }
            # Get track ids to put in playlist
            track_ids = []
            for track in tracks:
                track_query = {"spotify.track_id": track["track_id"]}
                # Find or create track
                mongo_track = db.tracks.find_one_and_update(
                    track_query,
                    {"$set": clean_track(track)},
                    upsert=True,
                    return_document=True,
                )
                track_ids.append(mongo_track.get("_id"))
            # Update playlist
            db.playlists.update_one(
                playlist_query,
                {"$set": {"tracks": track_ids, "time": datetime.now()}},
                upsert=True,
            )


def clean_track(track: dict) -> dict:
    """
    Function to clean up the given track dictionary by reorganizing and removing unnecessary fields.
    Takes a dictionary representing a track and returns a new cleaned-up dictionary.

    Args:
        track (dict): A dictionary representing a track.

    Returns:
        dict: A cleaned-up dictionary representing a track.
    """
    new_track = {}
    # Move analsis to separate field
    new_track["analysis"] = track
    # Remove unnecessary fields
    del new_track["analysis"]["type"]
    del new_track["analysis"]["id"]
    # move track attributes to track field
    new_track["track_name"] = new_track["analysis"]["track_name"]
    del new_track["analysis"]["track_name"]
    new_track["artist_name"] = new_track["analysis"]["artist_name"]
    del new_track["analysis"]["artist_name"]
    new_track["album_name"] = new_track["analysis"]["album_name"]
    del new_track["analysis"]["album_name"]
    # move spotify_specific attributes to own field
    new_track["spotify"] = {}
    new_track["spotify"]["track_id"] = new_track["analysis"]["track_id"]
    del new_track["analysis"]["track_id"]
    new_track["spotify"]["uri"] = new_track["analysis"]["uri"]
    del new_track["analysis"]["uri"]
    new_track["spotify"]["track_href"] = new_track["analysis"]["track_href"]
    del new_track["analysis"]["track_href"]

    return new_track


if __name__ == "__main__":
    main()
