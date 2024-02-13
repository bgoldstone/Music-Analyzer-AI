import requests
import re
import os
import csv
from bs4 import BeautifulSoup
from typing import Dict, List
#pip install beautifulsoup4 requests

def clean_text(text):
    text = text.lower()
    
    # removes remaster from text
    if(' remaster' in text):
        text_split = text.split(" - ",1)
        text = text_split[0] # just the part before the remaster
    
    # removes spaces
    text = text.replace(' ','')

    # removes parenthesis and inside if there's a feature
    text = re.sub(r'\(feat\..*?\)', '', text)

    # removes parenthesis but not inside
    text = re.sub(r'[()]', '', text)

    # removes puncuation
    text = re.sub(r'[.\-,?"[\]\']', '', text)

    return text

def grab_songs_from_csv():
    # this path works for my computer, temporary to start the crawler
    path = "/Users/12037/OneDrive/Documents/GitHub/Project-Sound/song_data/"

    # all subfolders in song_data folder
    dir_list = os.listdir(path) 

    # key is user
    # value is list of valid csv files
    csv_files = {}

    # populate users into dictionary with empty list
    for user in dir_list:
        csv_files[user] = list()

    # for each subfolder in folder
    i = 0
    for item in dir_list:
        # combine links
        files_in_each_user = os.listdir(path+item)
        #print(files_in_each_user)

        for file in files_in_each_user:
            # if correct csv file, add to list
            if('_details' not in file) and ('_ids' in file):
                # if dictionary empty
                csv_files[dir_list[i]].append(file)

        i += 1
    print(csv_files)

    # key is artist
    # value is list of songs
    songs_dict ={}

    # for each key
    for user in csv_files:
        # for each item in value list
        for csv_file_name in csv_files[user]:
            # directory to csv
            file_name = "/Users/12037/OneDrive/Documents/GitHub/Project-Sound/song_data/" + user +"/"+csv_file_name
            with open(file_name, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)

                for row in reader:
                    if(row != []):
                        artist = clean_text(row[2])
                        song_title = clean_text(row[1])

                        if artist not in songs_dict:
                            # set to disregard duplicates
                            songs_dict[artist] = set([song_title])
                        else:
                            songs_dict[artist].add(song_title)
    for key,val in songs_dict.items():
        print()
        print(key,val)
                
grab_songs_from_csv()