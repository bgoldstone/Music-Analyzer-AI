import pandas as pd
import os
import numpy as np
import ijson
import sys
import matplotlib
import matplotlib.pyplot as plt

DIRECTORY = "Daeshaun"  # Ex: "Daeshaun"
filename = (
    "Sad_Songs_track_details.json"  # "Lofi_Anime_Openings_track_details.json"
)
file_path = os.path.join("song_data", DIRECTORY, filename)

song_info = []
stand_vect = [({'happy': 19.722225599999994, 'sad': -19.722225599999994, 'intense': 143.98899992674365, 'mild': -143.98899992674365, 'danceability': 0.647}, 'Happy - From "Despicable Me 2"', '60nZcImufyMA1MKQY3dcCH'), ({'happy': 2.0000000000000052e-07, 'sad': -2.0000000000000052e-07, 'intense': -5.0613370864, 'mild': 5.0613370864, 'danceability': 0.468}, "Cruel Angel's Thesis but is it okay if it's lofi?", '221o9DvmsX6zOIG8BbP3nz'), ({'happy': -5.006553600000000017, 'sad': 5.006553600000000017, 'intense': 10.637991392150001, 'mild': -10.637991392150001, 'danceability': 0.447}, 'Unholy Confessions', '78XFPcFYN8YFOHjtVwnPsl'), ({'happy': -7.451940799999999, 'sad': 7.451940799999999, 'intense': -1.0585302068395999, 'mild': 1.0585302068395999, 'danceability': 0.467}, 'Everybody Hurts', '6PypGyiu0Y2lCDBN1XZEnP')]

stand_vect_dict = {
    "happy" : [({'happy': 19.722225599999994, 'sad': -19.722225599999994, 'intense': 143.98899992674365, 'mild': -143.98899992674365, 'danceability': 0.647}, 'Happy - From "Despicable Me 2"', '60nZcImufyMA1MKQY3dcCH')],
    "chill": [({'happy': 2.0000000000000052e-07, 'sad': -2.0000000000000052e-07, 'intense': -5.0613370864, 'mild': 5.0613370864, 'danceability': 0.468}, "Cruel Angel's Thesis but is it okay if it's lofi?", '221o9DvmsX6zOIG8BbP3nz')],
    "stressing": [({'happy': -5.006553600000000017, 'sad': 5.006553600000000017, 'intense': 10.637991392150001, 'mild': -10.637991392150001, 'danceability': 0.447}, 'Unholy Confessions', '78XFPcFYN8YFOHjtVwnPsl')],
    "sad": [({'happy': -7.451940799999999, 'sad': 7.451940799999999, 'intense': -1.0585302068395999, 'mild': 1.0585302068395999, 'danceability': 0.467}, 'Everybody Hurts', '6PypGyiu0Y2lCDBN1XZEnP'), ({'happy': -0.0009826000000000025, 'sad': 0.0009826000000000025, 'intense': 86.75278244360685, 'mild': -86.75278244360685, 'danceability': 0.652}, 'Let Me Down Slowly', '2qxmye6gAegTMjLKEBoR3d')],
}


def process_data(df):
    # Process each DataFrame. `df` is a dictionary of the song's properties. Ex: {"danceability": 0.647, "energy": 0.822,..."album_name": "G I R L"}.
    # For loop is used to access dict key and value
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
    emotionVectors["danceability"] = float(danceability)
    # Calculate vectors based on song properties
    song_info.append(calc_mood_from_details(float(tempo), float(valence), float(energy), track_name, track_id, emotionVectors))

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


def calc_mood_from_details(tempo, valence, energy, name, track_id, vectors):
    # Incorporating valence into mood vectors:
    # Increase the "happy" vector component and decrease the "sad" vector component based on valence level.
    vectors["happy"] += scale_valence(valence)
    vectors["sad"] -= scale_valence(valence)
    #
    # Incorporating energy into mood vectors:
    # Increase the "intense" vector component and decrease the "mild" vector component based on energy level.
    vectors["intense"] += scale_energy(energy) 
    vectors["mild"] -= scale_energy(energy) 
    #
    # Incorporating tempo into mood vectors:
    # Increase the "intense" vector component if tempo is high, else adjust "sad" based on the absolute value of scaled tempo.
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

        # avg_happiness
        # avg_chill
        # avg_stressing
        # avg_sadness

        # see cosine between each song in standard songs
        # for song in song_info:
        #     print(f"Song name: {song[1]}")
        #     print(f"Song dimensions: {song}")
        #     P1 = np.array(list(song[0].values()))
            
        #     for quadrant in stand_vect_dict:
        #         for each_song in stand_vect_dict[quadrant]:
        #             P2 = np.array(list(each_song[0].values()))
        #             print(each_song[1], end=": ")
        #             print(cosine_similarity(P1, P2))
        #     print("-----------------------------")

        for song in song_info:
            print(f"Song name: {song[1]}")
            print(f"Song dimensions: {song}")
            P1 = np.array(list(song[0].values()))
            
            for quadrant in stand_vect_dict:
                sum = 0
                print(quadrant, end=": ")
                for each_song in stand_vect_dict[quadrant]:
                    P2 = np.array(list(each_song[0].values()))
                    # print(each_song[1], end=": \n")
                    # print(cosine_similarity(P1, P2))
                    sum += cosine_similarity(P1, P2)
                print(sum / len(stand_vect_dict[quadrant]))
            print("-----------------------------")

    else:
        print("File not found:", file_path)
        return 0


if __name__ == "__main__":
    main()