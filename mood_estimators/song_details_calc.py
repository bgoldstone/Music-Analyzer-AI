import pandas as pd
import os
import numpy as np
import ijson
import json
import sys
import matplotlib
import matplotlib.pyplot as plt
import bertai
import dotenv
from pymongo import MongoClient
from max_heap import MaxHeap

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

def main(group):
    client = get_db_connection()
    dict_DB = import_tracks(client)
    heap = MaxHeap()

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
            # sum = 0
            # print(quadrant, end=": ")
            # for each_song in stand_vect_dict[quadrant]:
            #     P2 = np.array(list(each_song[0].values()))
            #     sum += cosine_similarity(P1, P2)
            # print(sum / len(stand_vect_dict[quadrant]))
            # similarity = sum / len(stand_vect_dict[quadrant])
            # heap.insert((similarity))
            if quadrant == group:
                sum = 0
                print(quadrant, end=": ")
                for each_song in stand_vect_dict[quadrant]:
                    P2 = np.array(list(each_song[0].values()))
                    sum += cosine_similarity(P1, P2)
                print(sum / len(stand_vect_dict[quadrant]))
                similarity = sum / len(stand_vect_dict[quadrant])
                heap.insert((similarity, track["track_name"], track["artist_name"]))
        print("-----------------------------")

    heap.print_sorted_heap()

def import_emotions_predict(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            keys = list(data.keys())[:2]

            if (keys[0] == "sadness") or (keys[0] == "disappointment") or (keys[0] == "grief") or (keys[0] == "remorse") or (keys[0] == "embarrassment"):
                return "sad"
            elif (keys[0] == "joy") or (keys[0] == "amusement") or (keys[0] == "surprise") or (keys[0] == "love") or (keys[0] == "excitement") or (keys[0] == "gratitude") or (keys[0] == "pride") or (keys[0] == "relief"):
                return "happy"
            elif (keys[0] == "neutral") or (keys[0] == "curiosity") or (keys[0] == "approval") or (keys[0] == "admiration") or (keys[0] == "realization") or (keys[0] == "optimism") or (keys[0] == "desire") or (keys[0] == "relief"):
                return "chill"
            elif (keys[0] == "anger") or (keys[0] == "annoyance") or (keys[0] == "disapproval") or (keys[0] == "disgust") or (keys[0] == "fear") or (keys[0] == "confusion") or (keys[0] == "caring") or (keys[0] == "nervousness"):
                return "stressing"

    except FileNotFoundError:
        return "File not found"
    except json.JSONDecodeError:
        return "Invalid JSON format"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    two_sentiments =  import_emotions_predict('mood_estimators\\emotion_predictions.json')
    main(two_sentiments)