import pandas as pd
import os
import numpy as np
import ijson
import sys
import matplotlib
import matplotlib.pyplot as plt
import bertai
import dotenv
import certifi
from pymongo import MongoClient

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

def import_tracks(db: MongoClient, updateAll = False):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    if updateAll:
        return list(db.tracks.find({}))
    else:
        # print(list(db.tracks.find({"vector": {"$exists": False}})))
        return list(db.tracks.find({"vector": {"$exists": False}}))

def process_data_DB(df, track_id, senti_analyis):
    """Process data from database for each track.

    Args:
        df (dict): Dictionary containing song properties.
        track_id (str): Track ID.
        track_name (str): Track name.
    """
    # Process each DataFrame. `df` is a dictionary of the song's properties. Ex: {"danceability": 0.647, "energy": 0.822,..."album_name": "G I R L"}.
    # For loop is used to access dict key and value
    track_id = track_id
    tempo = float(df["tempo"])
    valence = float(df["valence"])
    energy = float(df["energy"])
    danceability = df["danceability"]
    speechiness = df["speechiness"]

    emotion_dimensions = {
    "happy": 0,
    "sad": 0,
    "intense": 0,
    "mild": 0,
    "danceability": 0,
    }

    # Set danceabiltity & speechiness
    emotion_dimensions["danceability"] = float(danceability)
    emotion_dimensions["speechiness"] = float(speechiness)
    # Calculate vectors based on song properties
    song_info.append(calc_mood_from_details(track_id, emotion_dimensions, senti_analyis, tempo, valence, energy))

def scale_tempo(tempo):
    """Scale tempo.

    Args:
        tempo (float): Tempo value.

    Returns:
        float: Scaled tempo.
    """
    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return 0.00004 * (tempo - 90) ** 3

def scale_energy(energy):
    """Scale energy.

    Args:
        energy (float): Energy value.

    Returns:
        float: Scaled energy.
    """
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (20 * (energy - 0.50) ** 3) * 40

def scale_valence(valence):
    """Scale valence.

    Args:
        valence (float): Valence value.

    Returns:
        float: Scaled valence.
    """
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (20 * (valence - 0.50) ** 3) * 40

def import_lyrics(db: MongoClient, spotify_id):
    """Import lyrics from the database.

    Args:
        db (MongoClient): The MongoDB client. 
        id: The spotify song ID

    Returns:
        A string representing the song's lyrics
    """
    try:
        entry = (list(db.lyrics.find({"track_id": spotify_id}))[0])
        return entry["sentient_analysis"]
    except:
        return None


def calc_mood_from_details(track_id, vectors, sentiment_analysis, tempo, valence, energy):
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
    # Increase the "happy" vector component and decrease the "sad" vector component based on valence level.
    vectors["happy"] += round(scale_valence(valence), 3)
    vectors["sad"] -= round(scale_valence(valence), 3)
    #
    # Incorporating energy into mood vectors:
    # Increase the "intense" vector component and decrease the "mild" vector component based on energy level.
    vectors["intense"] += round(scale_energy(energy) , 3)
    vectors["mild"] -= round(scale_energy(energy) , 3)
    #
    # Incorporating tempo into mood vectors:
    # Increase the "intense" vector component if tempo is high, else adjust "sad" based on the absolute value of scaled tempo.
    vectors["intense"] += round(scale_tempo(tempo), 3) 
    vectors["mild"] -= round(scale_tempo(tempo), 3)

    # Incorporates an analysis of lyrics using bertai; tuples: happy_percentage, sad_percentage, mixed_percentage, no_impact_percentage
    try:
        if (sentiment_analysis["no_impact_percentage"] != 0) or (sentiment_analysis != None):
            print("Success: ", sentiment_analysis, track_id)
            baseNum = 25
            # Modify dimension values based on bert.ai sentiment analysis. 
            vectors["happy"] += (baseNum * sentiment_analysis["positive_percentage"])
            vectors["sad"] += (baseNum * sentiment_analysis["negative_percentage"])
            # Mixed percentage increases both dimensions
            vectors["happy"] += (baseNum * sentiment_analysis["mixed_percentage"])
            vectors["sad"] += (baseNum * sentiment_analysis["mixed_percentage"])
    except:
        pass
    
    return(vectors, track_id)

def get_db_connection() -> MongoClient | None:
    """Creates and returns db connection.

    Returns:
        MongoClient | None: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, ".env"))
    mongo_user = dotenv.dotenv_values().get("MONGO_USER")
    mongo_password = dotenv.dotenv_values().get("MONGO_PASSWORD")
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/"
    client = MongoClient(mongo_uri,tlsCAFile=certifi.where())
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
# Change to True if all song vector
dict_DB = import_tracks(client)

def main():
    for item in dict_DB:
        sentiment_analyis = import_lyrics(client, item["spotify"]["track_id"])
        process_data_DB(item["analysis"], item["spotify"]["track_id"], sentiment_analyis)
        # print(item["analysis"], item["spotify"]["track_id"], item["track_name"])

    for song in song_info:
        # print(f"Song ID: {song[1]}")
        # print(f"Song dimensions: {song}")
        # print("-----------------------------")
        load_vectors(client, song[0], song[1])

if __name__ == "__main__":
    main()