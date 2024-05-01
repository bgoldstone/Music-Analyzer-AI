import os
import certifi
import numpy as np
import json
import random
import dotenv
from pymongo import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = '5c787e0eccd246ba9c4500f755bff00b'
client_secret = 'a9b2fc8b4eac4f219aaa8dd852e98b1c'
redirect_uri = 'http://localhost:8000/oauth/spotify'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= client_id,
                                               client_secret= client_secret,
                                               redirect_uri= redirect_uri,
                                               scope='playlist-modify-public'))

try:
    from max_heap import MaxHeap
except ImportError:
    from mood_estimators.max_heap import MaxHeap

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

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

def import_tracks(db: MongoClient, query = {}):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.
        query (dict, optional): The query to filter tracks. Defaults to {}.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find(query))

def import_standard_songs(db: MongoClient, emotion):
    """Import standard songs from the database based on emotion.

    Args:
        db (MongoClient): The MongoDB client.
        emotion (str): The emotion to filter standard songs.

    Returns:
        list: List of tuples containing song vectors and track IDs.
    """
    tracks = list(db.tracks.find({"standard": emotion}))
    return [(track["vector"], track["spotify"]["track_id"]) for track in tracks]

def cosine_similarity(vector1, vector2):
    """Calculate the cosine similarity between two vectors.

    Args:
        vector1 (np.ndarray): The first vector.
        vector2 (np.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    dot_product = np.dot(vector1, vector2)
    magnitude_vector1 = np.linalg.norm(vector1)
    magnitude_vector2 = np.linalg.norm(vector2)
    return dot_product / (magnitude_vector1 * magnitude_vector2)

def main(group, numReturned = 500, playlistNum = 40):
    """Main function to calculate similarity rankings of songs based on emotions.

    Args:
        group (list): List of emotions.

    Returns:
        None
    """
    client = get_db_connection()
    dict_DB = import_tracks(client)
    heap = MaxHeap()

    stand_vect_dict = {
        "happy" : import_standard_songs(client, "happy"),
        "sad": import_standard_songs(client, "sad"),
        "chill": import_standard_songs(client, "chill"),
        "stressing": import_standard_songs(client, "stressing"),
    }

    for track in dict_DB:
        # print(f"Song name: {track["track_name"]} by {track["artist_name"]}")
        # print(f"Song dimensions: {track["vector"]}")
        P1 = np.array(list(track["vector"].values()))
        
        rank = []
        for each_sentiment in group:
            for quadrant in stand_vect_dict:
                if quadrant == each_sentiment:
                    sum = 0

                    for each_song in stand_vect_dict[quadrant]:
                        P2 = np.array(list(each_song[0].values()))
                        sum += cosine_similarity(P1, P2)

                    # similarity = round((sum / len(stand_vect_dict[quadrant])), 3)
                    similarity = round((sum / len(stand_vect_dict[quadrant])), 4)
                    # similarity = (sum / len(stand_vect_dict[quadrant]))
                    # print(quadrant, ":" , similarity)
                    rank.append(similarity)

        heap.insert((rank[0], rank[1], rank[2], rank[3], track["spotify"]["track_id"], track["track_name"], track["artist_name"]))

    # heap.print_sorted_heap(20)
    top_songs = []
    for i in range(numReturned):
        #print(i, ") ",heap.extract_max())
        each_track = (heap.extract_max())
        top_songs.append({"track_id": each_track[4], "track_name":each_track[5], "artist_name": each_track[6]})

        # top_songs.append({"track_id": track["spotify"]["track_id"], "track_name": track["track_name"], "artist_name": track["artist_name"]})
    
    

    # print(random.sample(top_songs, playlistNum))
    return random.sample(top_songs, playlistNum)

def import_emotions_predict(json_file_path):
    """Import predicted emotions from a JSON file.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        list | str: List of top predicted emotions or error message.
    """
    top_emotions = []
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            keys = list(data.keys())[:4]

            for key in keys:
                if (key == "joy") or (key == "amusement") or (key == "surprise") or (key == "love") or (key == "excitement") or (key == "gratitude") or (key == "pride") or (key == "relief"):
                    top_emotions.append("happy")
                elif (key == "sadness") or (key == "disappointment") or (key == "grief") or (key == "remorse") or (key == "embarrassment"):
                    top_emotions.append("sad")
                elif (key == "neutral") or (key == "curiosity") or (key == "approval") or (key == "admiration") or (key == "realization") or (key == "optimism") or (key == "desire"):
                    top_emotions.append("chill")
                elif (key == "anger") or (key == "annoyance") or (key == "disapproval") or (key == "disgust") or (key == "fear") or (key == "confusion") or (key == "caring") or (key == "nervousness"):
                    top_emotions.append("stressing")

        return top_emotions

    except FileNotFoundError:
        return "File not found"
    except json.JSONDecodeError:
        return "Invalid JSON format"
    except Exception as e:
        return f"An error occurred: {e}"

def generate_playlist_data_struct(name,description):
    playlist = sp.user_playlist_create(sp.me()['id'], name, public=True, description=description)
    return playlist['id']

def create_playlist(songs_dict):
    # list of song IDs
    song_ids = [id['track_id'] for id in songs_dict]

    playlist_id = generate_playlist_data_struct('SoundSmith test','Stop making playlists, Chris')

    for track in song_ids:
        song_ids.append(track['spotify']['track_id'])
    
    sp.playlist_add_items(playlist_id, song_ids)


if __name__ == "__main__":
    sentiments = import_emotions_predict('mood_estimators\\emotion_predictions.json')
    sentiments = ["stressing", "stressing", "chill", "chill"]
    songs_dict = main(sentiments)
    create_playlist(songs_dict)