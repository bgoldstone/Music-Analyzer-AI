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
#     "Standard_songs_track_details.json"  # "Lofi_Anime_Openings_track_details.json"
# )

# file_path = os.path.join("song_data", DIRECTORY, filename)

def import_tracks(db: MongoClient):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find({}))


def process_data(df):
    """Process data for each track.

    Args:
        df (dict): Dictionary containing song properties.
    """
    # Process each DataFrame. `df` is a dictionary of the song's properties. Ex: {"danceability": 0.647, "energy": 0.822,..."album_name": "G I R L"}.
    # For loop is used to access dict key and value
    track_name = df["track_name"]
    track_id = df["track_id"]
    tempo = df["tempo"]
    valence = df["valence"]
    energy = df["energy"]
    danceability = df["danceability"]

    emotion_dimensions = {
    "positive": 0,
    "negative": 0,
    "intense": 0,
    "mild": 0,
    "danceability": 0,
    }

    # Set danceabiltity
    emotion_dimensions["danceability"] = float(danceability)
    # Calculate vectors based on song properties
    song_info.append(calc_mood_from_details(float(tempo), float(valence), float(energy), track_id, emotion_dimensions))

def process_data_DB(df, track_id, text):
    """Process data from database for each track.

    Args:
        df (dict): Dictionary containing song properties.
        track_id (str): Track ID.
        track_name (str): Track name.
    """
    # Process each DataFrame. `df` is a dictionary of the song's properties. Ex: {"danceability": 0.647, "energy": 0.822,..."album_name": "G I R L"}.
    # For loop is used to access dict key and value
    track_name = track_name
    track_id = track_id
    tempo = df["tempo"]
    valence = df["valence"]
    energy = df["energy"]
    danceability = df["danceability"]

    emotion_dimensions = {
    "positive": 0,
    "negative": 0,
    "intense": 0,
    "mild": 0,
    "danceability": 0,
    }

    # Set danceabiltity
    emotion_dimensions["danceability"] = float(danceability)
    # Calculate vectors based on song properties
    song_info.append(calc_mood_from_details(float(tempo), float(valence), float(energy), track_id, emotion_dimensions, text))

def scale_tempo(tempo):
    """Scale tempo.

    Args:
        tempo (float): Tempo value.

    Returns:
        float: Scaled tempo.
    """
    # 70-90 bpm is the range where it is unclear that a song is positive or negative based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return 0.0001 * (tempo - 90) ** 3

def scale_energy(energy):
    """Scale energy.

    Args:
        energy (float): Energy value.

    Returns:
        float: Scaled energy.
    """
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is positive or negative
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (50 * (energy - 0.60) ** 3) * 40

def scale_valence(valence):
    """Scale valence.

    Args:
        valence (float): Valence value.

    Returns:
        float: Scaled valence.
    """
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is positive or negative
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (50 * (valence - 0.60) ** 3) * 40

def import_lyrics(db: MongoClient, spotify_id):
    """Import lyrics from the database.

    Args:
        db (MongoClient): The MongoDB client. 
        id: The spotify song ID

    Returns:
        A string representing the song's lyrics
    """
    entry = (list(db.lyrics.find({"track_id": spotify_id}))[0])
    return entry["lyrics"]

def calc_mood_from_details(tempo, valence, energy, track_id, vectors, text):
    """Calculate mood vectors based on song details.

    Args:
        tempo (float): Tempo value.
        valence (float): Valence value.
        energy (float): Energy value.
        name (str): Track name.
        track_id (str): Track ID.
        vectors (dict): Emotion vectors.

    Returns:
        tuple: Mood vectors, track ID, and track name.
    """
    # Incorporating valence into mood vectors:
    # Increase the "positive" vector component and decrease the "negative" vector component based on valence level.
    vectors["positive"] += round(scale_valence(valence), 3)
    vectors["negative"] -= round(scale_valence(valence), 3)
    #
    # Incorporating energy into mood vectors:
    # Increase the "intense" vector component and decrease the "mild" vector component based on energy level.
    vectors["intense"] += round(scale_energy(energy) , 3)
    vectors["mild"] -= round(scale_energy(energy) , 3)
    #
    # Incorporating tempo into mood vectors:
    # Increase the "intense" vector component if tempo is high, else adjust "negative" based on the absolute value of scaled tempo.
    vectors["intense"] += round(scale_tempo(tempo), 3) 
    vectors["mild"] -= round(scale_tempo(tempo), 3)

    # Incorporates an analysis of lyrics using bertai; tuples: positive_percentage, negative_percentage, mixed_percentage, no_impact_percentage
    # track_lyrics = import_lyrics(client)
    # baseNum = 20
    # lyrics_emotions = bertai.get_lyrics_mood()
    # # Modify dimension values based on bert.ai sentiment analysis. 
    # vectors["positive"] += (baseNum * (lyrics_emotions[0] / 100))
    # vectors["negative"] += (baseNum * (lyrics_emotions[1] / 100))
    # # Mixed percentage increases both dimensions
    # vectors["positive"] += (baseNum * (lyrics_emotions[2] / 100))
    # vectors["negative"] += (baseNum * (lyrics_emotions[2] / 100))
    
    vectors["positive"] += (baseNum * (25 / 100))
    vectors["negative"] += (baseNum * (50 / 100))
    # Mixed percentage increases both dimensions
    vectors["positive"] += (baseNum * (25 / 100))
    vectors["negative"] += (baseNum * (25 / 100))
    
    return(vectors, track_id, name)

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



def load_vectors(db: MongoClient, vector, id) -> None:
    """Load vectors into the database.

    Args:
        db (MongoClient): The MongoDB client.
        vector (dict): The vector to be loaded.
        id (str): The ID of the track.
    """
    track_query = {"spotify.track_id": id}

    # Find or create track
    mongo_track = db.tracks.find_one_and_update(
        track_query,
        {"$set": {"vector": vector}},
        upsert=True,
        return_document=True,
    )

song_info = []
client = get_db_connection()
dict_DB = import_tracks(client)

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
    #         print("-----------------------------")
    #         #
    #         client = get_db_connection()
    #         load_vectors(client, song[0], song[1])

    # else:
    #     print("File not found:", file_path)
    #     return 0
    # Open the JSON file
    for item in dict_DB:
        track_lyrics = import_lyrics(client, item["spotify"]["track_id"])
        process_data_DB(item["analysis"], item["spotify"]["track_id"], import_lyrics(client, item["spotify"]["track_id"]))
        # print(item["analysis"], item["spotify"]["track_id"], item["track_name"])

    for song in song_info:
        print(f"Song name: {song[2]}")
        print(f"Song dimensions: {song}")
        print("-----------------------------")
        load_vectors(client, song[0], song[1])

if __name__ == "__main__":
    main()