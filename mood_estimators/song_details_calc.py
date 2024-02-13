import pandas as pd
import os
import os.path as path

DIRECTORY = 'YOUR_DIRECTORY' # Ex: "Daeshaun"

def read_csv(file_name):
    for chunk in pd.read_csv(file_name, chunksize=10000):
        yield chunk

for df in read_csv("large_file.csv"):
    process_dataframe(df)