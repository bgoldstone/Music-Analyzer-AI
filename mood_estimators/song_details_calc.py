import pandas as pd
import os
import numpy as np
import ijson
import sys
import matplotlib
import matplotlib.pyplot as plt


DIRECTORY = "Daeshaun"  # Ex: "Daeshaun"
filename = (
    "Lofi_Anime_Openings_track_details.json"  # "Lofi Anime Openings_track_details.json"
)
file_path = os.path.join("song_data", DIRECTORY, filename)

# Dictionary format:
# string(key) = tuple(value)
# "name of song" = (valence, arousal)
labeled_songs = {}
song_info = []

# Coordinates for all vectors in graph
emotionCords = {
    "Stressing": (0.30, 120),
    "Boring": (0.25, -130),
    "Expressionless": (0.30, -130),
    "Expressive": (0.70, 130),
    "Amusing": (0.80, 90),
    "Relaxing": (0.70, -130),
}


# Compute Euclidean Distance in Python
def calc_Euc_Distance(valence, arousal):
    # `P1` is the vector with the song's valence and arousal
    P1 = np.array((valence, arousal))
    # Set shortestDict to nearest vector to nothing
    shortestDist = float("inf")
    nearestVector = ""
    # Check the Euclidean Distance from song to all labels
    # Find the shortest distance
    for emotion in emotionCords:
        P2 = np.array(emotionCords[emotion])
        temp = P1 - P2

        euclid_dist = np.sqrt(np.dot(temp, temp))
        # print(euclid_dist)

        if euclid_dist < shortestDist:
            shortestDist = euclid_dist
            nearestVector = emotion

    # print("Nearest emotion is ",  nearestVector, ". Distance: ",  shortestDist)
    return (nearestVector, shortestDist)


def process_data(df):
    # Process each DataFrame, `df.values` represent all rows in the csv file.
    # For loop is used to access each row of data in pandas dataframe
    track_name = df["track_name"]
    track_id = df["track_id"]
    tempo = df["tempo"]
    valence = df["valence"]
    energy = df["energy"]
    song_info = [
        calc_mood_from_details(
            track_name, track_id, int(tempo), int(valence), int(energy)
        )
    ]

    for song in song_info:
        labeled_songs[song[1]] = (song[0], song[1]) + calc_Euc_Distance(
            song[0], int(valence)
        )


def scale_tempo(tempo):
    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return ((0.0004 * (tempo - 80) ** 2) * 30) + 1


def scale_energy(energy):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return ((5 * (energy * -0.50) ** 2) * 5) + 1


def calc_mood_from_details(name, track_id, tempo, valence, energy):
    # Energy level based on `tempo` and `energy` params
    arousal = 0

    # Check how tempo should affect arousal level
    if tempo > 120:
        arousal += scale_tempo(tempo)

    elif tempo >= 90 and tempo <= 120:
        arousal += scale_tempo(tempo)

    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    elif tempo < 90 and tempo > 70:
        arousal += scale_tempo(tempo)
        arousal -= scale_tempo(tempo)

    else:
        arousal -= scale_tempo(tempo)

    # Check how energy should affect arousal level
    if energy > 0.75:
        arousal += scale_energy(energy)

    elif energy > 0.50:
        arousal += scale_energy(energy)

    elif energy > 0.40:
        arousal -= scale_energy(energy)
    else:
        arousal -= 2 * scale_energy(energy)

    # Now check the valence level:
    # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
    # Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric),
    # while tracks with low valence sound more negative (e.g. sad, depressed, angry).

    # if valence is positive, check arousal level
    printVal = False
    if valence > 0.5:
        if printVal == True:
            if arousal > 0:
                print(name + ": Upbeat, cheery", str(arousal), str(valence))
            else:
                print(name + ": Relaxing, happy", str(arousal), str(valence))
    # valence is negative, check arousal level
    else:
        if printVal == True:
            if arousal < 0:
                print(name + ": Stressing/Urgent", str(arousal), str(valence))
            else:
                print(name + ": Relaxing, sad", str(arousal), str(valence))

    return (arousal, name)


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

        # arousal, name of song, label, distance from nearest label
        # print([(value[0], key, value[2], value[3] ) for key, value in labeled_songs.items()])
        return [
            (value[0], key, value[2], value[3]) for key, value in labeled_songs.items()
        ]

    else:
        print("File not found:", file_path)
        return 0


if __name__ == "__main__":
    main()
