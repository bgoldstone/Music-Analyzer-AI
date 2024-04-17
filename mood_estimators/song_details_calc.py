import pandas as pd
import os
import numpy as np
import ijson
import sys
import matplotlib
import matplotlib.pyplot as plt
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

def import_tracks(db: MongoClient, query = {}):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find(query))

def import_standard_songs(db: MongoClient, emotion):
    tracks = list(db.tracks.find({"standard": emotion}))
    return [(track["vector"], track["spotify"]["track_id"]) for track in tracks]

def cosine_similarity(vector1, vector2):
    """Calculate the cosine similarity between two vectors.

    Args:
        vector1 (np.ndarray): The first vector.
        vector2 (np.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    dot_product = np.dot(vector1, vector2)
    magnitude_vector1 = np.linalg.norm(vector1)
    magnitude_vector2 = np.linalg.norm(vector2)
    return dot_product / (magnitude_vector1 * magnitude_vector2)

def main():
    client = get_db_connection()
    dict_DB = import_tracks(client)

    stand_vect_dict = {
        "positive" : import_standard_songs(client, "happy"),
        "chill": import_standard_songs(client, "chill"),
        "stressing": import_standard_songs(client, "stressing"),
        "negative": import_standard_songs(client, "sad"),
    }

    for track in dict_DB:
        print(f"Song name: {track["track_name"]} by {track["artist_name"]}")
        print(f"Song dimensions: {track["vector"]}")
        P1 = np.array(list(track["vector"].values()))
        
        for quadrant in stand_vect_dict:
            sum = 0
            print(quadrant, end=": ")
            for each_song in stand_vect_dict[quadrant]:
                P2 = np.array(list(each_song[0].values()))
                sum += cosine_similarity(P1, P2)
            print(sum / len(stand_vect_dict[quadrant]))
        print("-----------------------------")

if __name__ == "__main__":
    main()