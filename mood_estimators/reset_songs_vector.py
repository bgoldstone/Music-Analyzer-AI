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

DIRECTORY = "Daeshaun"  # Ex: "Daeshaun"
filename = (
    "Standard_songs_track_details.json"  # "Lofi_Anime_Openings_track_details.json"
)

file_path = os.path.join("song_data", DIRECTORY, filename)

song_info = []

def process_data(df):
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
    song_info.append(calc_mood_from_details(float(tempo), float(valence), float(energy), track_name, track_id, emotion_dimensions))

def scale_tempo(tempo):
    # 70-90 bpm is the range where it is unclear that a song is positive or negative based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return 0.0004 * (tempo - 90) ** 3


def scale_energy(energy):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is positive or negative
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (5 * (energy - 0.50) ** 3) * 40

def scale_valence(valence):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is positive or negative
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (5 * (valence - 0.50) ** 3) * 40


def calc_mood_from_details(tempo, valence, energy, name, track_id, vectors):
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

    # Incorporates an analysis of lyrics using bertai; tuples: positive_count, negative_count, mixed_count, no_impact_count
    lyrics_emotions = bertai.get_lyrics_mood()

    for eachPercent in lyrics_emotions:
        index = 0
        if index == 0:
            vectors["positive"] += (16 * (eachPercent / 100))
        elif index == 1:
            vectors["negative"] += (16 * (eachPercent / 100))
        elif index == 2:
            vectors["positive"] += (16 * (eachPercent / 100))
            vectors["negative"] += (16 * (eachPercent / 100))
        elif index == 3:
            vectors["positive"] -= (16 * (eachPercent / 100))
            vectors["negative"] -= (16 * (eachPercent / 100))

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
    track_query = {"spotify.track_id": id}

    # Find or create track
    mongo_track = db.tracks.find_one_and_update(
        track_query,
        {"$set": {"vector": vector}},
        upsert=True,
        return_document=True,
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


def main():
    # Get the data(audio features from spotify) from the json
    if os.path.exists(file_path):
        # Open the JSON file
        with open(file_path, "r") as file:
            # Parse the JSON objects one by one
            parser = ijson.items(file, "item")

            # Iterate over the JSON objects
            for item in parser:
                process_data(item)

        for song in song_info:
            print(f"Song name: {song[2]}")
            print(f"Song dimensions: {song}")
            print("-----------------------------")
            #
            client = get_db_connection()
            load_vectors(client, song[0], song[1])

    else:
        print("File not found:", file_path)
        return 0

if __name__ == "__main__":
    main()