import re
import os
import csv
import requests
import time
from bs4 import BeautifulSoup
from typing import Dict, List

valid_links = 0
invalid_links = 0
total_links = 0

def clean_text(text: str,) -> str:
    text = text.lower()
    
    # removes remaster / remastered from text
    if(' remaster' in text):
        text_split = text.split(' - ',1)
        text = text_split[0] # keep the part before the remaster
    
    # removes spaces
    text = text.replace(' ','')

    # removes parenthesis and inside if there's a feature
    text = re.sub(r'\(feat\..*?\)', '', text)

    # removes parenthesis but not inside
    text = re.sub(r'[()]', '', text)

    # removes puncuation
    text = re.sub(r'[.\-\/,?"[\]\']', '', text)

    return text

def grab_songs_from_csv() -> dict[str]:
    # current project folder joined with \song_data
    path = os.path.join(os.getcwd(),'song_data')

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
        files_in_each_user = os.listdir(os.path.join(path,item))

        for file in files_in_each_user:
            # if correct csv file, add to list
            if('_details' not in file) and ('_ids' in file):
                # if dictionary empty
                csv_files[dir_list[i]].append(file)
        i += 1

    # key is artist
    # value is list of songs
    songs_dict ={}

    # for each key
    for user in csv_files:
        # for each item in value list
        for csv_file_name in csv_files[user]:
            # directory to csv
            first = True
            file_name = os.path.join(os.getcwd(),'song_data',user,csv_file_name)

            with open(file_name, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)

                for row in reader:
                    # skips empty rows and first row
                    if(row != [])and(not first):
                        artist = clean_text(row[2])
                        song_title = clean_text(row[1])

                        #print(song_title)
                        if artist not in songs_dict:
                            # set() to disregard duplicates
                            songs_dict[artist] = set([song_title])
                        else:
                            songs_dict[artist].add(song_title)
                    first = False
    return songs_dict

# creates links to parse, from azlyrics.com
def create_links(songs_dict: dict,) -> set[str]:
    # start of each link
    start_url = "https://www.azlyrics.com/lyrics/"
    
    links = set()

    for artist, songs in songs_dict.items():
        for song in songs:
            url = start_url + artist + '/' + song + '.html'
            links.add(url)
    
    return links

def store_lyrics(links: set):

    global valid_links
    global invalid_links
    global total_links

    already_parsed = []

    i =0

    for link in links:
        if(i<1):
            total_links += 1
            try:
                response = requests.get(link)

                if(response.status_code == 200): #if response was successful
                    print('valid:',link)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    print(soup)
                    already_parsed.append(response)
                    valid_links += 1
                else:
                    #print('invalid:',link)
                    invalid_links += 1

            except Exception as e:
                pass
            i += 1
        else:
            break

print()
songs_dict = grab_songs_from_csv()
song_links = create_links(songs_dict)
store_lyrics(song_links)

print("\nInvalid links:",invalid_links)
print("Valid links:",valid_links)
print("Total links:",total_links)