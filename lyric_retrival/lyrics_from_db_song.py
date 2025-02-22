from typing import Dict, List, Tuple
from pymongo import MongoClient
import dotenv
import os
import time
import lyricsgenius
import certifi
import re
import json

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

genius_key = "dZCHAObV2X7ZCH4QN2bewuX7lAVoVHedaot3cNn8l_dpwtSwWEaK1cHg8TrbhDtq"
genius_token='4Os3tEbxKSqR_gE76OqwUY3TTQVO11MVLDy14ZmmrC4AS0SygKak8dpgZy3wb5pe'
genius = lyricsgenius.Genius(genius_token)

def get_db_connection() -> MongoClient | None:
    """Creates and returns db connection.

    Returns:
        MongoClient | None: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, ".env"))
    mongo_user = dotenv.dotenv_values().get("MONGO_USER")
    mongo_password = dotenv.dotenv_values().get("MONGO_PASSWORD")
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/"
    client = MongoClient(mongo_uri,tlsCAFile=certifi.where())
    db = client.soundsmith
    try:
        db.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return
    return db

def import_tracks(db: MongoClient) -> List[Dict]:
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find({}))

def get_song_and_artist_and_id_from_db(tracks_from_db: List[Dict]) -> List[Tuple[str, str, int]]:
    """
    Extracts artist name, song title, and Spotify track ID from a list of dictionaries representing tracks from a database.

    Args:
        tracks_from_db (list): A list of dictionaries where each dictionary represents a track from the database.
                           Each dictionary should contain keys 'spotify' with sub-key 'track_id', 'artist_name',
                           and 'track_name' for the relevant information.

    Returns:
    list: A list of tuples, where each tuple contains (artist_name, track_name, track_id) extracted from the input list
          of dictionaries.
    """

    # stores tuples in the form (artist, song_title)
    tracks_to_get_lyrics = []
    
    # iterate over each dictionary
    for db_track in tracks_from_db:
        song_id: int = db_track['spotify']['track_id']
        artist: str = db_track['artist_name']
        song_title: str = db_track['track_name']
        tracks_to_get_lyrics.append((artist,song_title,song_id))
    
    return tracks_to_get_lyrics

def clean_lyrics(txt: str) -> str:
    """
    Cleans lyrics text by removing text within square brackets, artist name at the beginning of the text,
    and any newline characters at the beginning of the string.

    Args:
        txt (str): The input lyrics text to be cleaned.

    Returns:
        str: The cleaned lyrics text.
    """
    no_brackets: str = re.sub(r'\[.*?\]', '', txt)
    no_artist: str = re.sub(r'^(.*?\n)','',no_brackets)
    return no_artist

def grab_lyrics(tracks: List[Tuple[str, str, int]]) -> Dict[str, Dict[str, Dict[int, str]]]:
    """
    Retrieve lyrics for specified tracks using the Genius API.

    Args:
        tracks (list): A list of tuples containing track information (artist, title, ID).

    Returns:
        dict: A nested dictionary containing retrieved lyrics organized by artist, song title, and ID.
    """
    song_lyrics = {}

    START_INDEX: int = 6800
    FINISH_INDEX: int = len(tracks)

    for i in range(START_INDEX, FINISH_INDEX):
        cur_artist = tracks[i][0]
        song_title = tracks[i][1]
        song_id = tracks[i][2]
        # the delay for each API call. Initialized to 1 and increased if there's a time out.
        delay = 1

        time.sleep(delay)
        print('\n', f"Working on track {i}: {cur_artist} {song_title}.")

        attempt = 0
        max_attempts = 3  # Maximum number of attempts for each song
        
        while attempt <= max_attempts:
            try:
                song = genius.search_song(song_title, artist=cur_artist)
                if song is not None and song.lyrics is not None:
                    break  # If song is found and lyrics are available, exit the loop
                else:
                    time.sleep(delay)
            except Exception as e:
                print(f"Error occurred: {e}")
                print("Retrying...")
                delay += 3
                time.sleep(delay)
            finally:
                attempt += 1
        
        if song is None or song.lyrics is None:
            print(f"Track {i} is not in the Genius database.")
        else:
            # Successful lyric grab
            lyrics_clean = clean_lyrics(song.lyrics)
            
            # Store track information and cleaned lyrics in a nested dictionary
            lyrics = lyrics_clean

            if(cur_artist not in song_lyrics):
                song_lyrics[cur_artist] = {song_title : {song_id : lyrics}}
            else:
                if song_title not in song_lyrics[cur_artist]:
                    song_lyrics[cur_artist][song_title] = {song_id: lyrics}
                else:
                    song_lyrics[cur_artist][song_title][song_id] = lyrics
        
    return song_lyrics

def load_lyrics(db: MongoClient, id, lyrics) -> None:
    """
    Upsert lyrics for a track in the specified MongoDB database.

    Args:
        db (MongoClient): The MongoClient instance connected to the MongoDB database.
        id: The unique identifier of the track.
        lyrics: The lyrics to be inserted for the track.

    Returns:
        dict: The document representing the track after the update or insertion.
    """

    track_query = {"track_id": id}

    # Find or create track
    mongo_track = db.lyrics.find_one_and_update(
        track_query,
        {"$set": {"lyrics": lyrics}},
        upsert=True,
        return_document=True,
    )

def main() -> None:
    """
    Main function to retrieve and store lyrics for tracks from a database.

    Returns:
        None
    """
    db = get_db_connection()

    tracks_from_db = import_tracks(db)
    tracks_to_get_lyrics = get_song_and_artist_and_id_from_db(tracks_from_db)
    lyrics_dict = grab_lyrics(tracks_to_get_lyrics)

    # Old code used for testing dictionary with json file
    
    """
    #with open("lyric_retrival\\lyrics.json", "w") as json_file:
        #json.dump(lyrics_dict, json_file, indent=4)
    #print(lyrics_dict)
    """

    for artist, artist_info in lyrics_dict.items():
        for song,tuple in artist_info.items():
            for id, lyrics in tuple.items():
                load_lyrics(db, id, lyrics)

if __name__ == "__main__":
    main()