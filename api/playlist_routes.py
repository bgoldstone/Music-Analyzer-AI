import token
from typing import Dict
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
import sys
import pathlib
from transformers import pipeline
from mood_estimators import song_details_calc
from spotipy import oauth2, Spotify
from dotenv import load_dotenv
import json
from fastapi import APIRouter, Request, Response, WebSocket, FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from requests import request
from spotipy import oauth2, Spotify
import dotenv
from urllib.parse import urlencode
import spotipy.util as util
import os
import json
import spotipy
from spotify_data_retrival.data_retrival import get_track_details
from database.load_data import load_playlists


sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from api.models import GetPlaylist, Playlist, PlaylistGenerate
from database.crud import (
    create_playlist,
    delete_playlist,
    get_playlist_with_tracks,
    update_playlist_by_id,
)

CONFIG = dotenv.dotenv_values("spotify_data_retrival/.env")

oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])
sp_oauth = oauth2.SpotifyOAuth(
    CONFIG.get("SPOTIFY_CLIENT_ID"),
    CONFIG.get("SPOTIFY_CLIENT_SECRET"),
    CONFIG.get("SPOTIFY_REDIRECT_URI"),
    scope=CONFIG.get("SPOTIFY_SCOPE").split(","),
    cache_path=CONFIG.get("SPOTIFY_CACHE_PATH"),
)

playlist_router = APIRouter(prefix="/playlists", tags=["playlists"])


@playlist_router.get(
    "/{playlist_name}",
    response_description="Get a single playlist by name",
)

def get_playlist(playlist_name: str, request: Request) -> Dict:
    """
    Get a single playlist by name.

    Args:
        playlist_name (str): The name of the playlist to retrieve.
        request (Request): The request object containing the application database.

    Returns:
        Dict: The playlist with the specified name, including the "_id" and "user_id" fields converted to strings.

    Raises:
        HTTPException: If the playlist with the specified name is not found.

    """

    playlist = get_playlist_with_tracks(playlist_name, request.app.database)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist {playlist_name} not found",
        )
    print(playlist)
    playlist["_id"] = str(playlist["_id"])
    playlist["user_id"] = str(playlist["user_id"])
    return playlist



@playlist_router.post(
    "/",
    response_description="Create a new playlist",
)
def create_new_playlist(playlist: Playlist, request: Request) -> Dict:
    """
    Create a new playlist.

    Args:
        playlist (Playlist): The playlist object containing the details of the new playlist.
        request (Request): The request object containing the application database.

    Returns:
        Dict: The created playlist with the "_id" and "user_id" fields converted to strings.
    """
    playlist = create_playlist(jsonable_encoder(playlist), request.app.database)
    return playlist


@playlist_router.put(
    "/{playlist_id}",
    response_description="Update a playlist",
)
def update_playlist(playlist_id: str, playlist: Dict, request: Request) -> Dict:
    """
    A function to update a playlist by its ID using the provided playlist data and request information.

    Args:
        playlist_id (str): The ID of the playlist to update.
        playlist (Dict): The updated playlist data.
        request (Request): The request object containing the application database.

    Returns:
        Dict: The updated playlist after the changes are applied.
    """
    playlist = update_playlist_by_id(playlist_id, playlist, request.app.database)
    return playlist


@playlist_router.delete(
    "/{playlist_id}",
    response_description="Delete a playlist",
)
def delete_playlist_by_id(playlist_id: str, request: Request) -> None:
    """
    A function to delete a playlist by its ID using the provided playlist ID and request information.
    
    Args:
        playlist_id (str): The ID of the playlist to delete.
        request (Request): The request object containing the application database.

    Returns:
        None
    """
    delete_playlist(playlist_id, request.app.database)


@playlist_router.post(
    "/generate",
    response_description="Generate a new playlist with AI",
)
def generate_playlist(playlist: PlaylistGenerate) -> Dict:
    # Initialize the text classification pipeline
    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
    """
    Generate a new playlist with AI based on the provided PlaylistGenerate object.

    Args:
        playlist (PlaylistGenerate): The PlaylistGenerate object containing the description.

    Returns:
        Dict: A dictionary containing the generated tracks for the playlist.
    """

    # Classify emotions for the given sentence
    predictions = classifier(playlist.description)

    # Extract the emotion labels and scores from the predictions
    emotion_labels = [emotion['label'] for emotion in predictions[0]]
    emotion_scores = [emotion['score'] for emotion in predictions[0]]

    # Combine emotion labels and scores into a dictionary
    emotion_predictions = dict(zip(emotion_labels, emotion_scores))

    # Write the dictionary to a JSON file
    output_file = "mood_estimators/emotion_predictions.json"
    with open(output_file, 'w') as f:
        json.dump(emotion_predictions, f, indent=4)

    print("Emotion predictions have been saved to", output_file)
    
    # Import emotion predictions
    emotions_predict = song_details_calc.import_emotions_predict('mood_estimators/emotion_predictions.json')
    print(emotions_predict)
    
    # Generate tracks based on emotion predictions
    tracks = song_details_calc.main(emotions_predict)

    # Create Spotify playlist using stored emotion predictions
    sp = Spotify(auth_manager=oauth2.SpotifyOAuth(
        client_id=CONFIG["SPOTIFY_CLIENT_ID"],
        client_secret=CONFIG["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=CONFIG["SPOTIFY_REDIRECT_URI"],
        scope=CONFIG["SPOTIFY_SCOPE"].split(","),
        cache_path=CONFIG["SPOTIFY_CACHE_PATH"]
    ))

    # Function to create a new playlist on Spotify
    def create_playlist(name, description=None, public=True):
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user=user_id, name=name, public=public, description=description)
        return playlist['id']

    # Function to add tracks to a Spotify playlist
    def add_tracks_to_playlist(playlist_id, tracks):
        # Extract track IDs from the tracks dictionary
        track_ids = [track['track_id'] for track in tracks]
        # Add tracks to the playlist
        sp.playlist_add_items(playlist_id, track_ids)
    
    # Load generated playlist from JSON file
    with open("playlist_generated/finished_playlist.json", "r") as f:
        tracks = json.load(f)

    # Create playlist on Spotify
    playlist_id = create_playlist("SoundSmith Playlist", playlist.description)
    
    # Add tracks to the playlist
    add_tracks_to_playlist(playlist_id, tracks)

    print(f"Playlist 'SoundSmith Playlist' created with ID: {playlist_id}")

    return {'tracks': tracks}

@playlist_router.put(
    "jwt_token/{jwt_token}",
    response_description="Grabs users Oauth access token from the frontend"              
)
def get_jwt(jwt_token: str, request: Request) -> Dict:
    jwt_user = {'jwt_token': jwt_token}
    return jwt_user

'''
def store_playlist(playlist_name, playlist_description, json_file_path):
    # Initialize Spotipy client with Authorization Code Flow
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                   client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                                                   redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                                                   scope="playlist-modify-public"))

    def create_playlist(name, description=None, public=True):
        user_id = sp.me()['id']  # Retrieve the authenticated user's ID
        playlist = sp.user_playlist_create(user=user_id, name=name, public=public, description=description)
        return playlist['id']

    def add_tracks_to_playlist(playlist_id, track_ids):
        sp.playlist_add_items(playlist_id, track_ids)

    # Create playlist
    playlist_id = create_playlist(playlist_name, playlist_description)

    # Load track information from JSON
    with open(json_file_path) as f:
        track_info = json.load(f)

    # Extract track IDs
    track_ids = [track['track_id'] for track in track_info]

    # Add tracks to the playlist
    add_tracks_to_playlist(playlist_id, track_ids)
    
    return playlist_id

def store_playlist_run():
        # Load environment variables from .env file
    load_dotenv()

    playlist_name = 'SoundSmithPlaylist'
    playlist_description = 'test'  # Optional
    json_file_path = 'finished_playlist.json'

    playlist_id = store_playlist(playlist_name, playlist_description, json_file_path)
    print(f"Playlist '{playlist_name}' created with ID: {playlist_id}")
'''