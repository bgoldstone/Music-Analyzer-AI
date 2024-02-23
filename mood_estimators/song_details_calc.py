import pandas as pd
import os

DIRECTORY = 'Daeshaun'  # Ex: "Daeshaun"
filename = 'Anime_lofi_track_details.csv' # "Anime_lofi_track_details.csv"
file_path = os.path.join('song_data', DIRECTORY, filename)

# Uncomment next two lines to adjust pandas display options to show all columns and rows
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)


def process_dataframe(df):
    # Process each DataFrame, `df.values` represent all rows in the csv file.
    # For loop is used to access each row of data in pandas dataframe
    song_info = [calc_mood_from_details( row[19],row[14],row[10],row[9], row[1]) for row in df.values]


def scale_tempo(tempo):
    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    # Therefore, equation  output smaller values between that range
    # Outliners(60bpm or 120bpm) have exponentially higher outputs
    return ((0.0004 * (tempo - 80 ) ** 2) * 50) + 1

def scale_energy(energy):
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, equation  output smaller values between that range
    # Outliners(0.10 or 0.9) have exponentially higher outputs
    return ((5 * (energy * - 0.50) ** 2) * 5) + 1
 
def calc_mood_from_details(name, track_href, tempo, valance, energy):
    # Energy level based on `tempo` and `energy` params

    energy_level = {
    "high_arousal": 0,
    "low_arousal": 0,
    }

    # Check how tempo should affect arousal level
    if (tempo > 120):
        energy_level["high_arousal"] += scale_tempo(tempo)
        energy_level["low_arousal"] -= scale_tempo(tempo)

    elif (tempo >= 90 and tempo <= 120):
        energy_level["high_arousal"] += scale_tempo(tempo)
        energy_level["low_arousal"] -= scale_tempo(tempo)

    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    elif (tempo < 90 and tempo > 70):
        energy_level["high_arousal"] -= scale_tempo(tempo)
        energy_level["low_arousal"] -= scale_tempo(tempo)
    
    else: 
        energy_level["high_arousal"] -= scale_tempo(tempo)
        energy_level["low_arousal"] += scale_tempo(tempo)
    
    # Check how energy should affect arousal level
    if (energy > .75):
        energy_level["high_arousal"] += scale_energy(energy)
        energy_level["low_arousal"] -= scale_energy(energy)

    elif (energy > .50):
        energy_level["high_arousal"] -= scale_energy(energy)
        energy_level["low_arousal"] += scale_energy(energy)

    elif (energy > .25):
        energy_level["high_arousal"] -= scale_energy(energy)
        energy_level["low_arousal"] += scale_energy(energy)
    else:
        energy_level["high_arousal"] -= scale_energy(energy)
        energy_level["low_arousal"] += scale_energy(energy)

    # Now check the valence level:
    # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. 
    # Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), 
    # while tracks with low valence sound more negative (e.g. sad, depressed, angry).

    # if valance is positive, check arousal level
    if (valance > 0.5):
        if (max(energy_level, key=energy_level.get) == "high_arousal"):
            print(name + ": Upbeat, cheery")
        else:
            print(name + ": Relaxing, happy")
    # valance is negative, check arousal level
    else:
        if (max(energy_level, key=energy_level.get) == "high_arousal"):
            print(name + ": Stressing/Urgent")
        else:
            print(name + ": Relaxing, sad")

    # print(energy_level, "\n")
    
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