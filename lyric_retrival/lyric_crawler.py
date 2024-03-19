import re
import os
import csv
import requests
import time
from bs4 import BeautifulSoup
from typing import Dict, List
import json

valid_links: int = 0
invalid_links: int = 0
total_links: int = 0

def clean_text(text: str,) -> str:
    """
    Cleans the input text by performing various text processing operations.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
        
    """

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
    text = re.sub(r'[.\=\-\/,?"[\]\']', '', text)

    return text

def grab_songs_from_csv() -> dict[str]:
    """
    Retrieves songs and artists from CSV files and organizes them into a dictionary.

    Returns:
        dict[str]: A dictionary where keys are artists and values are sets of song titles.

    Comments:
        This function scans the 'song_data' folder for subfolders corresponding to users.
        It then populates a dictionary ('csv_files') where each user is a key mapped to a list of valid CSV files in their subfolder.
        Next, it creates an empty dictionary ('songs_dict') to store songs and artists.
        It iterates through the 'csv_files' dictionary, extracting songs and artists from each CSV file and populating 'songs_dict'.
        The 'clean_text' function is used to preprocess the artist and song title strings.
        The function returns the populated 'songs_dict'.
    """

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
    """
    Creates a set of URLs for lyrics based on a dictionary of songs and artists.

    Args:
        songs_dict (dict): A dictionary where keys are artists and values are lists of song titles.

    Returns:
        set[str]: A set of URLs for lyrics corresponding to the songs in the input dictionary.

    Comments:
        This function takes a dictionary containing artists as keys and lists of song titles as values.
        It constructs URLs for the lyrics of each song by appending the artist name and song title to a base URL.
        The base URL is 'https://www.azlyrics.com/lyrics/'.
        Each URL is added to a set to ensure uniqueness.
        The function returns the set of generated URLs.
    """

    start_url = "https://www.azlyrics.com/lyrics/"
    
    # initialize empty set to store URLs
    links = set()

    for artist, songs in songs_dict.items():
        for song in songs:
            # create links and too set
            url = start_url + artist + '/' + song + '.html'
            links.add(url)
    
    return links

def store_lyrics(links: set):
    """
    Retrieves lyrics from a set of links and stores them in a JSON file.

    Args:
        links (set): A set of URLs containing links to azlyrics.com.

    Returns:
        None

    Comments:
        This function iterates over the provided set of links, retrieving lyrics from each link and storing them in a JSON file.
        It limits the number of links processed to a maximum of MAX_LINKS to avoid overloading the system.
        The function keeps track of the number of valid and invalid links processed.
        It utilizes BeautifulSoup to parse the HTML content of each link and extract the lyrics.
        The lyrics are stored in a dictionary where the link serves as the key and the lyrics as the value.
        Finally, the lyrics dictionary is converted to JSON format and saved to a file named 'lyrics.json'.
    """

    global valid_links
    global invalid_links
    global total_links
    
    MAX_LINKS = 5
    already_parsed = []
    lyrics_dict = {}

    i = 0
    for link in links:
        if(i<MAX_LINKS):
            total_links += 1
            try:
                time.sleep(3)
                response = requests.get(link)

                if(response.status_code == 200): #if response was successful
                    print('valid:',link)
                    valid_links += 1
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # finds the appropriate <div> containing the lyrics, always after two breaks
                    br1 = soup.find('br')
                    br2 = br1.find_next('br')

                    lyrics_div = br2.find_next_sibling('div')

                    if lyrics_div:
                        # extract lyrics and store them in database
                        lyrics_text = lyrics_div.text.strip()
                        lyrics_dict[link] = lyrics_text
                        print(lyrics_text)

                    already_parsed.append(response)
                else:
                    print('invalid:',link)
                    invalid_links += 1

            except Exception as e:
                pass
            i += 1
        else:
            break
    
    # stores lyrics_dict in json file
    json_object = json.dumps(lyrics_dict, indent=1)

    with open("lyric_retrival\\lyrics.json", "w") as outfile:
        outfile.write(json_object)

songs_dict = grab_songs_from_csv()
song_links = create_links(songs_dict)
store_lyrics(song_links)

print("\nInvalid links:",invalid_links)
print("Valid links:",valid_links)
print("Total links:",total_links)