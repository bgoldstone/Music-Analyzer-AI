import pandas as pd
import os
# import os.path as paths

DIRECTORY = 'Insert Name'  # Ex: "Daeshaun"
filename = 'Insert_playlist_details' # "Anime_lofi_track_details.csv"
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
    song_info = [calc_mood_from_details( row[19],row[14],row[10],row[9], row[1]) for row in df.values]

def mood():
    pass

def scale_tempo(tempo):
    # print(((0.0004 * (tempo - 80 ) ** 2) * 50) + 1)
    return ((0.0004 * (tempo - 80 ) ** 2) * 50) + 1
def scale_energy(energy):
    return ((5 * (energy * -0.5) ** 2) * 5) + 1
 
# 70-90 bpm is the range where it is unclear that a song is happy or sad
def calc_mood_from_details(name, track_href, tempo, valance, energy):
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
        emotions["Happiness"] += scale_tempo(tempo)
        emotions["Suprise"] += scale_tempo(tempo)
        emotions["Sadness"] -= scale_tempo(tempo)
        feelings["Tension"] += scale_tempo(tempo)
        feelings["Expressiveness"] += scale_tempo(tempo)

    elif (tempo >= 90 and tempo <= 120):
        emotions["Happiness"] += scale_tempo(tempo)
        emotions["Suprise"] += scale_tempo(tempo)
        emotions["Sadness"] -= scale_tempo(tempo)
        feelings["Tension"] += scale_tempo(tempo)
        feelings["Expressiveness"] += scale_tempo(tempo)
    # threshold between positive and negative emotions & feeling
    elif (tempo < 90 and tempo > 60):
        emotions["Happiness"] -= scale_tempo(tempo)
        emotions["Suprise"] -= scale_tempo(tempo)
        emotions["Sadness"] += scale_tempo(tempo)
        feelings["Tension"] += scale_tempo(tempo)
        feelings["Expressiveness"] += scale_tempo(tempo)
    
    else: 
        emotions["Happiness"] -= scale_tempo(tempo)
        emotions["Suprise"] -= scale_tempo(tempo)
        emotions["Sadness"] += scale_tempo(tempo)
        feelings["Tension"] += scale_tempo(tempo)
        feelings["Expressiveness"] += scale_tempo(tempo)

    # 
    if (energy > 0.9):
        emotions["Happiness"] += scale_energy(energy)
        emotions["Suprise"] += scale_energy(energy)
        emotions["Sadness"] -= scale_energy(energy)
        feelings["Tension"] += scale_energy(energy)
        feelings["Expressiveness"] += scale_energy(energy)

    elif (energy > .75):
        emotions["Happiness"] += scale_energy(energy)
        emotions["Suprise"] += scale_energy(energy)
        emotions["Sadness"] -= scale_energy(energy)
        feelings["Tension"] += scale_energy(energy)
        feelings["Expressiveness"] += scale_energy(energy)

    elif (energy > .50):
        emotions["Happiness"] -= scale_energy(energy)
        emotions["Suprise"] -= scale_energy(energy)
        emotions["Sadness"] += scale_energy(energy)
        feelings["Tension"] -=scale_energy(energy)
        feelings["Expressiveness"] -= scale_energy(energy)

    else:
        emotions["Happiness"] -= scale_energy(energy)
        emotions["Suprise"] -= scale_energy(energy)
        emotions["Sadness"] += scale_energy(energy)
        feelings["Tension"] -=scale_energy(energy)
        feelings["Expressiveness"] -= scale_energy(energy)

    if (valance > 0.5):
        if (max(emotions, key=emotions.get) == "Happiness"):
            print(name + ": Expressive")
        else:
            print(name + ": Relaxing")
    else:
        if (max(emotions, key=emotions.get) == "Happiness"):
            print(name + ": Stressing")
        else:
            print(name + ": Boring")

    print(emotions, "\n")
    


if os.path.exists(file_path):
    def read_csv(file_name):
        for chunk in pd.read_csv(file_name, chunksize=10000):
            yield chunk

    for df in read_csv(file_path):
        process_dataframe(df)
else:
    print("File not found:", file_path)