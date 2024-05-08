import os
import bertai
import dotenv
import certifi
from pymongo import MongoClient
from typing import List, Dict, Tuple, Optional

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

def import_tracks(db: MongoClient, updateAll: bool = False) -> List[dict]:
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.
        updateAll (bool, optional): Flag indicating whether to update all tracks. Defaults to False.

    Returns:
        List[dict]: List of tracks.
    """
    if updateAll:
        return list(db.tracks.find({}))
    else:
        return list(db.tracks.find({"vector": {"$exists": False}}))

def process_data_DB(df: Dict[str, float], track_id: str, sentiment_analysis: dict) -> None:
    """Process data from database for each track.

    Args:
        df (Dict[str, float]): Dictionary containing song properties.
        track_id (str): Track ID.
        sentiment_analysis (dict): Dictionary containing sentiment analysis.
    """
    # Process each DataFrame. `df` is a dictionary of the song's properties.
    # Extract tempo, valence, energy, danceability, and speechiness from the dictionary.
    tempo = float(df["tempo"])
    valence = float(df["valence"])
    energy = float(df["energy"])
    danceability = df["danceability"]
    speechiness = df["speechiness"]

    # Initialize emotion dimensions dictionary with default values
    emotion_dimensions = {
        "happy": 0,
        "sad": 0,
        "intense": 0,
        "mild": 0,
        "danceability": 0,
    }

    # Set danceability & speechiness
    emotion_dimensions["danceability"] = float(danceability)
    emotion_dimensions["speechiness"] = float(speechiness)
    
    # Calculate vectors based on song properties and sentiment analysis
    song_info.append(calc_mood_from_details(track_id, emotion_dimensions, sentiment_analysis, tempo, valence, energy))

def scale_tempo(tempo: float) -> float:
    """Scale tempo.

    Args:
        tempo (float): Tempo value.

    Returns:
        float: Scaled tempo.
    """
    # 70-90 bpm is the range where it is unclear that a song is happy or sad based on tempo
    # Therefore, the equation outputs smaller values between that range
    # Outliers (60bpm or 120bpm) have exponentially higher outputs
    return 0.00004 * (tempo - 90) ** 3

def scale_energy(energy: float) -> float:
    """Scale energy.

    Args:
        energy (float): Energy value.

    Returns:
        float: Scaled energy.
    """
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, the equation outputs smaller values between that range
    # Outliers (0.10 or 0.9) have exponentially higher outputs
    return (20 * (energy - 0.50) ** 3) * 40

def scale_valence(valence: float) -> float:
    """Scale valence.

    Args:
        valence (float): Valence value.

    Returns:
        float: Scaled valence.
    """
    # 0.40 - 0.60 energy level is the range where it is unclear that a song is happy or sad
    # Therefore, the equation outputs smaller values between that range
    # Outliers (0.10 or 0.9) have exponentially higher outputs
    return (20 * (valence - 0.50) ** 3) * 40

def import_lyrics(db: MongoClient, spotify_id: str) -> Optional[dict]:
    """Import lyrics from the database.

    Args:
        db (MongoClient): The MongoDB client.
        spotify_id (str): The Spotify song ID.

    Returns:
        dict: A dictionary representing the song's sentiment percentages for the lyrics.
        Or None if there isn't any.
    """
    try:
        entry = list(db.lyrics.find({"track_id": spotify_id}))[0]
        return entry["sentient_analysis"]
    except IndexError:
        return None
    except KeyError:
        return None

def calc_mood_from_details(track_id: str, vector: Dict[str, float], sentiment_analysis: Dict[str, float], tempo: float, valence: float, energy: float) -> Tuple[Dict[str, float], str]:
    """Calculate mood vector based on song details.

    Args:
        track_id (str): Track ID.
        vector (Dict[str, float]): Emotion vector.
        sentiment_analysis (Dict[str, float]): Sentiment analysis of lyrics.
        tempo (float): Tempo value.
        valence (float): Valence value.
        energy (float): Energy value.

    Returns:
        Tuple[Dict[str, float], str]: Mood vector, track ID.
    """
    # Incorporating valence into mood vector:
    # Increase the "happy" vector component and decrease the "sad" vector component based on valence level.
    vector["happy"] += round(scale_valence(valence), 3)
    vector["sad"] -= round(scale_valence(valence), 3)
    
    # Incorporating energy into mood vector:
    # Increase the "intense" vector component and decrease the "mild" vector component based on energy level.
    vector["intense"] += round(scale_energy(energy), 3)
    vector["mild"] -= round(scale_energy(energy), 3)
    
    # Incorporating tempo into mood vector:
    # Increase the "intense" vector component if tempo is high, else adjust "sad" based on the absolute value of scaled tempo.
    vector["intense"] += round(scale_tempo(tempo), 3)
    vector["mild"] -= round(scale_tempo(tempo), 3)

    # Incorporates an analysis of lyrics using bertai; tuples: happy_percentage, sad_percentage, mixed_percentage, no_impact_percentage
    try:
        if sentiment_analysis["no_impact_percentage"] != 0 or sentiment_analysis is not None:
            baseNum = 25
            # Modify dimension values based on bert.ai sentiment analysis.
            vector["happy"] += baseNum * sentiment_analysis.get("positive_percentage", 0)
            vector["sad"] += baseNum * sentiment_analysis.get("negative_percentage", 0)
            # Mixed percentage increases both dimensions
            vector["happy"] += baseNum * sentiment_analysis.get("mixed_percentage", 0)
            vector["sad"] += baseNum * sentiment_analysis.get("mixed_percentage", 0)
    # Ignore cases where sentiment_analysis does not exist
    except:
        pass
    
    return vector, track_id

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

def load_vectors(db: MongoClient, vector: dict, id: str) -> None:
    """Load vectors into the database.

    Args:
        db (MongoClient): The MongoDB client.
        vector (dict): The vector to be loaded.
        id (str): The ID of the track.
    """
    track_query = {"spotify.track_id": id}

    # Find or create track
    mongo_track = db.tracks.find_one_and_update(
        track_query,
        {"$set": {"vector": vector}},
        upsert=True,
        return_document=True,
    )

song_info = []

def main():
    """Main function for processing tracks and loading vectors into the database."""
    # Establish MongoDB connection
    client = get_db_connection()
    
    # Retrieve tracks from the database
    dict_DB = import_tracks(client, False)

    # Iterate through each track
    for item in dict_DB:
        # Import sentiment analysis from the database for the track
        sentiment_analysis = import_lyrics(client, item["spotify"]["track_id"])
        # Process data for the track from the database
        process_data_DB(item["analysis"], item["spotify"]["track_id"], sentiment_analysis)

    # Iterate through the processed song information
    for song in song_info:
        # Load vectors into the database for each song
        load_vectors(client, song[0], song[1])

if __name__ == "__main__":
    main()