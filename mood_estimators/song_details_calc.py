import pandas as pd
import os
# import os.path as paths

DIRECTORY = 'Daeshaun'  # Ex: "Daeshaun"
filename = 'Anime_lofi_track_details.csv' # "Anime_lofi_track_details.csv"
file_path = os.path.join('song_data', DIRECTORY, filename)
# Uncomment next two lines to adjust pandas display options to show all columns and rows
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)

# Set of dictionaries
all_songs = []

def process_dataframe(df):
    # Process each DataFrame, for example, print its head
    # for row in df.values:
        # song_info = [ for name, track_href, tempo, valance in ]
    # 19, 14, 10, 9
    song_info = [calc_mood_from_details( row[19],row[14],row[10],row[9]) for row in df.values]

def calc_mood_from_details(name, track_href, tempo, valance):
    emotions = {
    "Happiness": 0,
    "Suprise": 0,
    "Sadness": 0,
    }
    
    feelings = {
    "Tension": 0,
    "Expressiveness": 0,
    "Amusement": 0,
    "Attractiveness": 0,
    }

    if (tempo > 120):
        emotions["Happiness"] += 5
        emotions["Suprise"] += 5
        emotions["Sadness"] -= 5
        feelings["Tension"] += 5
        feelings["Expressiveness"] += 4

    elif (tempo >= 90 and tempo <= 120):
        emotions["Happiness"] += 3
        emotions["Suprise"] += 3
        emotions["Sadness"] -= 3
        feelings["Tension"] += 3
        feelings["Expressiveness"] += 2

    elif (tempo < 90 and tempo > 60):
        emotions["Happiness"] -= 3
        emotions["Suprise"] += 2
        emotions["Sadness"] += 3
        feelings["Tension"] += 2
        feelings["Expressiveness"] += 1

    # print(name, feelings)
    if (valance > .5):
        if (max(emotions, key=emotions.get) == "Happiness"):
            print(name + ": Expressive")
        else:
            print(name + "Relaxing")
    else:
        if (max(emotions, key=emotions.get) == "Happiness"):
            print(name + ": Stressing")
        else:
            print(name + "Boring")


if os.path.exists(file_path):
    def read_csv(file_name):
        for chunk in pd.read_csv(file_name, chunksize=10000):
            yield chunk

    for df in read_csv(file_path):
        process_dataframe(df)
else:
    print("File not found:", file_path)