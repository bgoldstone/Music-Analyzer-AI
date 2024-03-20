import pandas as pd
import os
import numpy as np
import ijson
import sys
import matplotlib
import matplotlib.pyplot as plt

DIRECTORY = "Daeshaun"  # Ex: "Daeshaun"
filename = (
    "R&B_track_details.json"  # "Lofi Anime Openings_track_details.json"
)
file_path = os.path.join("song_data", DIRECTORY, filename)

song_info = []

def process_data(df):
    # Process each DataFrame, `df.values` represent all rows in the csv file.
    # For loop is used to access each row of data in pandas dataframe
    track_name = df["track_name"]
    track_id = df["track_id"]
    tempo = df["tempo"]
    valence = df["valence"]
    energy = df["energy"]
    danceability = df["danceability"]

    emotionVectors = {
    "happy": 0,
    "sad": 0,
    "intense": 0,
    "mild": 0,
    "danceability": 0,
    }

    # Set danceabiltity
    emotionVectors["danceability"] = int(danceability)
    # Calculate vectors based on song properties
    song_info.append(calc_mood_from_details(track_name, track_id, emotionVectors, float(tempo), float(valence), float(energy)))

def scale_tempo(tempo):
    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return 0.0004 * (tempo - 90) ** 3


def scale_energy(energy):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (5 * (energy - 0.50) ** 3) * 40

def scale_valence(valence):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return (5 * (valence - 0.50) ** 3) * 40


def calc_mood_from_details(name, track_id, vectors, tempo, valence, energy):
    # Now check the valence level:
    # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
    # Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric),
    # while tracks with low valence sound more negative (e.g. sad, depressed, angry).
    vectors["happy"] += scale_valence(valence)
    vectors["sad"] -= scale_valence(valence)
    #
    vectors["intense"] += scale_energy(energy) 
    vectors["mild"] -= scale_energy(energy) 
    #
    vectors["intense"] += scale_tempo(tempo) 
    vectors["mild"] -= scale_tempo(tempo)
    return(vectors, name, track_id)

def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    magnitude_vector1 = np.linalg.norm(vector1)
    magnitude_vector2 = np.linalg.norm(vector2)
    return dot_product / (magnitude_vector1 * magnitude_vector2)


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
            # print(song)
            pass
        
        P1 = np.array(list(song_info[0][0].values()))

        for value in song_info:
            P2 = np.array(list(value[0].values()))
            print(value[1], end=": ")
            print(cosine_similarity(P1, P2))

    else:
        print("File not found:", file_path)
        return 0


if __name__ == "__main__":
    main()