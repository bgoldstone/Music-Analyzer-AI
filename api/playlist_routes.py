import token
from typing import Dict
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
import sys
import pathlib
from transformers import pipeline
from mood_estimators import song_details_calc
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import json

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from api.models import GetPlaylist, Playlist, PlaylistGenerate
from database.crud import (
    create_playlist,
    delete_playlist,
    get_playlist_with_tracks,
    update_playlist_by_id,
)

playlist_router = APIRouter(prefix="/playlists", tags=["playlists"])


@playlist_router.get(
    "/{playlist_name}",
    response_description="Get a single playlist by name",
)

def get_playlist(playlist_name: str, request: Request) -> Dict:
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
    playlist = create_playlist(jsonable_encoder(playlist), request.app.database)
    return playlist


@playlist_router.put(
    "/{playlist_id}",
    response_description="Update a playlist",
)
def update_playlist(playlist_id: str, playlist: Dict, request: Request) -> Dict:
    playlist = update_playlist_by_id(playlist_id, playlist, request.app.database)
    return playlist


@playlist_router.delete(
    "/{playlist_id}",
    response_description="Delete a playlist",
)
def delete_playlist_by_id(playlist_id: str, request: Request) -> None:
    delete_playlist(playlist_id, request.app.database)


@playlist_router.post(
    "/generate",
    response_description="Generate a new playlist with AI",
)
def generate_playlist(playlist: PlaylistGenerate) -> Dict:
    
    # Initialize the text classification pipeline
    classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

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
    emotions_predict = song_details_calc.import_emotions_predict('mood_estimators/emotion_predictions.json')
    print(emotions_predict)
    tracks = song_details_calc.main(emotions_predict)

    playlist_output_file = "playlist_generated/finished_playlist.json"
    with open(playlist_output_file, 'w') as f:
        finished_playlist =  json.dump(tracks, f, indent=4)
    print(f"Generated finished list: \n {finished_playlist}")

    return {'tracks': tracks}


@playlist_router.put(
    "jwt_token/{jwt_token}",
    response_description="Grabs users Oauth access token from the frontend"              
)
def get_jwt(jwt_token: str, request: Request) -> Dict:
    jwt_user = {'jwt_token': jwt_token}
    return jwt_user


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