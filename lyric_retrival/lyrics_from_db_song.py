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

def import_tracks(db: MongoClient):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find({}))

def get_song_and_artist_and_id_from_db(tracks_from_db):

    # stores tuples in the form (artist, song_title)
    tracks_to_get_lyrics = []
    
    # iterate over each dictionary
    for db_track in tracks_from_db:
        song_id = db_track['spotify']['track_id']
        artist = db_track['artist_name']
        song_title = db_track['track_name']
        tracks_to_get_lyrics.append((artist,song_title,song_id))
    
    return tracks_to_get_lyrics

def clean_lyrics(txt):
    no_brackets = re.sub(r'\[.*?\]', '', txt)
    no_artist = re.sub(r'^(.*?\n)','',no_brackets)
    return no_artist

def grab_lyrics(tracks):
    song_lyrics = {}

    for i in range(len(tracks)):
        if(i==6):
            break
        cur_artist = tracks[i][0]
        song_title = tracks[i][1]
        song_id = tracks[i][2]
        # the delay for each API call. Initialized to 3 and increased if there's a time out.
        delay = 3

        time.sleep(delay)
        print('\n', f"Working on track {i}: {cur_artist} {song_title}.")

        attempt = 0
        max_attempts = 3  # Maximum number of attempts for each song
        
        while attempt <= max_attempts:
            try:
                song = genius.search_song(song_title, artist=cur_artist)
                if song is not None and song.lyrics is not None:
                    break  # If song is found and lyrics are available, exit the loop
            except Exception as e:
                print(f"Error occurred: {e}")
                print("Retrying...")
                delay *= 3
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

def load_lyrics(db: MongoClient, id, lyrics):
    track_query = {"track_id": id}

    # Find or create track
    mongo_track = db.lyrics.find_one_and_update(
        track_query,
        {"$set": {"lyrics": lyrics}},
        upsert=True,
        return_document=True,
    )

def main():
    db = get_db_connection()

    tracks_from_db = import_tracks(db)
    tracks_to_get_lyrics = get_song_and_artist_and_id_from_db(tracks_from_db)
    lyrics_dict = grab_lyrics(tracks_to_get_lyrics)

    #with open("lyric_retrival\\lyrics.json", "w") as json_file:
        #json.dump(lyrics_dict, json_file, indent=4)
    #print(lyrics_dict)

    for artist, artist_info in lyrics_dict.items():
        for song,tuple in artist_info.items():
            for id, lyrics in tuple.items():
                print(song)
                print("id",id)
                print("lyrics",lyrics)
                print()
                #load_lyrics(db, id, lyrics)

if __name__ == "__main__":
    main()