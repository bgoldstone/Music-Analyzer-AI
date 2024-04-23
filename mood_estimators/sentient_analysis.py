import os
import bertai
import dotenv
from pymongo import MongoClient

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

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

def import_lyrics(db: MongoClient):
    """Import lyrics from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.lyrics.find({}))

def load_analysis(db: MongoClient, id, percentage) -> None:
    """Load vectors into the database.

    Args:
        db (MongoClient): The MongoDB client.
        vector (dict): The vector to be loaded.
        id (str): The ID of the track.
    """
    track_query = {"track_id": id}

    # Find or create track
    mongo_track = db.lyrics.find_one_and_update(
        track_query,
        {"$set": {"sentient_analysis": percentage}},
        upsert=True,
        return_document=True,
    )

def main():
    client = get_db_connection()
    lyrics = import_lyrics(client)

    for each_lyric in lyrics:
        try:
            sentient_analysis = bertai.get_lyrics_mood(each_lyric["lyrics"])
            load_analysis(client, each_lyric["track_id"], sentient_analysis)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()