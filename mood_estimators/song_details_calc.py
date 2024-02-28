import pandas as pd
import os
import numpy as np

DIRECTORY = 'Daeshaun'  # Ex: "Daeshaun"
filename = 'Anime_lofi_track_details.csv'  # "Anime_lofi_track_details.csv"
file_path = os.path.join('song_data', DIRECTORY, filename)

# Uncomment next two lines to adjust pandas display options to show all columns and rows
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)



emotionCords = {
    "Stressing": ( 120, 0.30),
    "Boring": ( -130, 0.25),
    "Expressionless": (-130, 0.30),
    "Expressive": (130 ,0.70),
    "Amusing": (90, 0.80),
    "Relaxing": (-130, 0.70)
}

# Compute Euclidean Distance in Python
def calc_Euc_Distance(arousal, valance):
    P1 = np.array((arousal, valance))

    shortestDist = float('inf')
    nearestVector = ""

    for emotion in emotionCords:
        P2 = np.array(emotionCords[emotion])
        temp = P1 - P2

        euclid_dist = np.sqrt(np.dot(temp.T, temp))
        print(euclid_dist)

        if euclid_dist < shortestDist:
            shortestDist = euclid_dist
            nearestVector = emotion

    print("Nearest emotion is ",  nearestVector, ". Distance: ",  shortestDist)

def process_dataframe(df):
    # Process each DataFrame, `df.values` represent all rows in the csv file.
    # For loop is used to access each row of data in pandas dataframe
    song_info = [calc_mood_from_details( row[19], row[12], row[10], row[9], row[1] ) for row in df.values]
    
    for song in song_info:
        print("Name: ", song[2])
        calc_Euc_Distance(song[0], song[1])

def scale_tempo(tempo):
    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return ((0.0004 * (tempo - 80) ** 2) * 30) + 1


def scale_energy(energy):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return ((5 * (energy * - 0.50) ** 2) * 5) + 1


def calc_mood_from_details(name, track_id, tempo, valance, energy):
    # Energy level based on `tempo` and `energy` params
    arousal = 0

    # Check how tempo should affect arousal level
    if (tempo > 120):
        arousal += scale_tempo(tempo)

    elif (tempo >= 90 and tempo <= 120):
        arousal += scale_tempo(tempo)

    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    elif (tempo < 90 and tempo > 70):
        arousal += scale_tempo(tempo)
        arousal -= scale_tempo(tempo)
    
    else: 
        arousal -= scale_tempo(tempo)

    
    # Check how energy should affect arousal level
    if (energy > .75):
        arousal += scale_energy(energy)

    elif (energy > .50):
        arousal += scale_energy(energy)

    elif (energy > .25):
        arousal -= (scale_energy(energy))
    else:
        arousal -= 2 * scale_energy(energy)

    # Now check the valence level:
    # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
    # Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric),
    # while tracks with low valence sound more negative (e.g. sad, depressed, angry).

    # if valance is positive, check arousal level
    printVal = False
    if (valance > 0.5):
        if (printVal == True):
            if (arousal > 0):
                print(name + ": Upbeat, cheery", str(arousal), str(valance))
            else:
                print(name + ": Relaxing, happy", str(arousal), str(valance))
    # valance is negative, check arousal level
    else:
        if (printVal == True):
            if (arousal < 0):
                print(name + ": Stressing/Urgent", str(arousal), str(valance))
            else:
                print(name + ": Relaxing, sad", str(arousal), str(valance))

    return (arousal, valance, name)


# Get the data(audio features from spotify) from the csv
if os.path.exists(file_path):
    # Rows are cut into chunks to speed up processing
    def read_csv(file_name):
        for chunk in pd.read_csv(file_name, chunksize=1000):
            yield chunk
    # Process a chunk
    for df in read_csv(file_path):
        process_dataframe(df)
else:
    print("File not found:", file_path)
