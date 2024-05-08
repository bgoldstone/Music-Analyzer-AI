import os
import certifi
import numpy as np
import json
import random
import dotenv
from pymongo import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Tuple, Union, Dict, Any

client_id: str = '5c787e0eccd246ba9c4500f755bff00b'
client_secret: str = 'a9b2fc8b4eac4f219aaa8dd852e98b1c'
redirect_uri: str = 'http://localhost:8000/oauth/spotify'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= client_id,
                                               client_secret= client_secret,
                                               redirect_uri= redirect_uri,
                                               scope='playlist-modify-public'))

try:
    from max_heap import MaxHeap
except ImportError:
    from mood_estimators.max_heap import MaxHeap

MONGO_URL: str = "soundsmith.x5y65kb.mongodb.net"

def get_db_connection() -> Union[MongoClient, None]:
    """Creates and returns db connection.

    Returns:
        MongoClient | None: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, ".env"))
    mongo_user: str = dotenv.dotenv_values().get("MONGO_USER")
    mongo_password: str = dotenv.dotenv_values().get("MONGO_PASSWORD")
    mongo_uri: str = f"mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/"
    client: Union[MongoClient, None] = MongoClient(mongo_uri,tlsCAFile=certifi.where())
    db: Any = client.soundsmith
    try:
        db.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return None
    return db

def import_tracks(db: MongoClient, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.
        query (dict, optional): The query to filter tracks. Defaults to {}.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find(query))

def import_standard_songs(db: MongoClient, emotion: str) -> List[Tuple[Dict[str, Any], str]]:
    """Import standard songs from the database based on emotion.

    Args:
        db (MongoClient): The MongoDB client.
        emotion (str): The emotion to filter standard songs.

    Returns:
        list: List of tuples containing song vectors and track IDs.
    """
    tracks: List[Dict[str, Any]] = list(db.tracks.find({"standard": emotion}))
    return [(track["vector"], track["spotify"]["track_id"]) for track in tracks]

def cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """Calculate the cosine similarity between two vectors.

    Args:
        vector1 (np.ndarray): The first vector.
        vector2 (np.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    try:
        dot_product: float = np.dot(vector1, vector2)
        magnitude_vector1: float = np.linalg.norm(vector1)
        magnitude_vector2: float = np.linalg.norm(vector2)
        return dot_product / (magnitude_vector1 * magnitude_vector2)
    except Exception as e:
        print(e)

def import_emotions_predict(json_file_path: str) -> List[str] | str:
    """Import predicted emotions from a JSON file.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        List[str] | str: List of top predicted emotions or error message.
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

def generate_playlist_data_struct(name: str, description: str) -> str:
    """Generate playlist data structure.

    Args:
        name (str): Name of the playlist.
        description (str): Description of the playlist.

    Returns:
        str: Playlist ID.
    """
    playlist = sp.user_playlist_create(sp.me()['id'], name, public=True, description=description)
    return playlist['id']

def create_playlist(songs_dict: List[Dict[str, str]]) -> None:
    """Create a playlist.

    Args:
        songs_dict (List[Dict[str, str]]): List of dictionaries containing song information.

    Returns:
        None
    """
    # list of song IDs
    song_ids = [id['track_id'] for id in songs_dict]

    playlist_id = generate_playlist_data_struct('SoundSmith test','Stop making playlists, Chris')

    for track in song_ids:
        song_ids.append(track['spotify']['track_id'])
    
    sp.playlist_add_items(playlist_id, song_ids)

def main(group: List[str], numReturned: int = 500, playlistNum: int = 40) -> List[Dict[str, str]]:
    """Main function to calculate similarity rankings of songs based on emotions.

    Args:
        group (list): List of emotions.
        numReturned (int): Number of top songs to return. Defaults to 500.
        playlistNum (int): Number of songs in the playlist. Defaults to 40.

    Returns:
        list: List of dictionaries containing top songs.
    """
    client: Union[MongoClient, None] = get_db_connection()
    dict_DB: List[Dict[str, Any]] = import_tracks(client)
    heap: MaxHeap = MaxHeap()

    stand_vect_dict: Dict[str, List[Tuple[Dict[str, Any], str]]] = {
        "happy" : import_standard_songs(client, "happy"),
        "sad": import_standard_songs(client, "sad"),
        "chill": import_standard_songs(client, "chill"),
        "stressing": import_standard_songs(client, "stressing"),
    }

    for track in dict_DB:
        P1: np.ndarray = np.array(list(track["vector"].values()))
        
        rank: List[float] = []
        for each_sentiment in group:
            for quadrant in stand_vect_dict:
                if quadrant == each_sentiment:
                    sum_: float = 0

                    for each_song in stand_vect_dict[quadrant]:
                        P2: np.ndarray = np.array(list(each_song[0].values()))
                        sum_ += cosine_similarity(P1, P2)

                    similarity: float = round((sum_ / len(stand_vect_dict[quadrant])), 4)
                    rank.append(similarity)

        heap.insert((rank[0], rank[1], rank[2], rank[3], track["spotify"]["track_id"], track["track_name"], track["artist_name"]))

    top_songs: List[Dict[str, str]] = []
    
    # for i in range(numReturned):
    #     each_track: Tuple[float, float, float, float, str, str, str] = heap.extract_max()
    #     top_songs.append({"track_id": each_track[4], "track_name":each_track[5], "artist_name": each_track[6]})
    #     print(i, ") ", each_track)
    
    for i in range(numReturned):
        each_track: Tuple[float, float, float, float, str, str, str] = heap.extract_max()
        track_id, track_name, artist_name = each_track[4], each_track[5], each_track[6]
        # Encode the strings as ASCII before printing
        # print(i, ") ", track_id.encode('ascii', 'ignore'), track_name.encode('ascii', 'ignore'), artist_name.encode('ascii', 'ignore'))
        top_songs.append({"track_id": track_id, "track_name": track_name, "artist_name": artist_name})
    
    return random.sample(top_songs, playlistNum)

if __name__ == "__main__":
    sentiments = import_emotions_predict('mood_estimators\\emotion_predictions.json')
    sentiments = ["stressing", "stressing", "chill", "chill"]
    main(sentiments)