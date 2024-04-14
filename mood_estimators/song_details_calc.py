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

# DIRECTORY = "Daeshaun"  # Ex: "Daeshaun"
# filename = (
#     "Sad_Songs_track_details.json"  # "Lofi_Anime_Openings_track_details.json"
# )
# file_path = os.path.join("song_data", DIRECTORY, filename)

song_info = []

stand_vect_dict = {
    "positive" : [({'positive': 19.722225599999994, 'negative': -19.722225599999994, 'intense': 143.98899992674365, 'mild': -143.98899992674365, 'danceability': 0.647}, 'Happy - From "Despicable Me 2"', '60nZcImufyMA1MKQY3dcCH')],
    "chill": [({'positive': 2.0000000000000052e-07, 'negative': -2.0000000000000052e-07, 'intense': -5.0613370864, 'mild': 5.0613370864, 'danceability': 0.468}, "Cruel Angel's Thesis but is it okay if it's lofi?", '221o9DvmsX6zOIG8BbP3nz')],
    "stressing": [({'positive': -5.006553600000000017, 'negative': 5.006553600000000017, 'intense': 10.637991392150001, 'mild': -10.637991392150001, 'danceability': 0.447}, 'Unholy Confessions', '78XFPcFYN8YFOHjtVwnPsl'), ({'positive': -1.6484816000000002, 'negative': 1.6484816000000002, 'intense': 17.488896165004796, 'mild': -17.488896165004796, 'danceability': 0.725}, 'Demon Slayer (Rengoku Theme)', '0eTQEpSLPnZhuahEuf1IE1')],
    "negative": [({'positive': -7.451940799999999, 'negative': 7.451940799999999, 'intense': -1.0585302068395999, 'mild': 1.0585302068395999, 'danceability': 0.467}, 'Everybody Hurts', '6PypGyiu0Y2lCDBN1XZEnP'), ({'positive': -0.0009826000000000025, 'negative': 0.0009826000000000025, 'intense': 86.75278244360685, 'mild': -86.75278244360685, 'danceability': 0.652}, 'Let Me Down Slowly', '2qxmye6gAegTMjLKEBoR3d'), ({'positive': -6.3108992, 'negative': 6.3108992, 'intense': -0.1848024869664003, 'mild': 0.1848024869664003, 'danceability': 0.418}, 'Stay With Me', '5Nm9ERjJZ5oyfXZTECKmRt')],
}

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

def import_tracks(db: MongoClient):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find({}))


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
    # # Get the data(audio features from spotify) from the json
    # if os.path.exists(file_path):
    #     # Open the JSON file
    #     with open(file_path, "r") as file:
    #         # Parse the JSON objects one by one
    #         parser = ijson.items(file, "item")

    #         # Iterate over the JSON objects
    #         for item in parser:
    #             process_data(item)

    #     for song in song_info:
    #         print(f"Song name: {song[2]}")
    #         print(f"Song dimensions: {song}")
    #         P1 = np.array(list(song[0].values()))
            
    #         for quadrant in stand_vect_dict:
    #             sum = 0
    #             print(quadrant, end=": ")
    #             for each_song in stand_vect_dict[quadrant]:
    #                 P2 = np.array(list(each_song[0].values()))
    #                 sum += cosine_similarity(P1, P2)
    #             print(sum / len(stand_vect_dict[quadrant]))
    #         print("-----------------------------")

    # else:
    #     print("File not found:", file_path)
    #     return 0

    client = get_db_connection()
    dict_DB = import_tracks(client)

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