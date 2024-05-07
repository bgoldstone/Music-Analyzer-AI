import pathlib
import sys
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
from auth import tokens
from database.crud import create_spotify_user, create_user, get_spotify_user

CONFIG = dotenv.dotenv_values("spotify_data_retrival/.env")

oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])
sp_oauth = oauth2.SpotifyOAuth(
    CONFIG.get("SPOTIFY_CLIENT_ID"),
    CONFIG.get("SPOTIFY_CLIENT_SECRET"),
    CONFIG.get("SPOTIFY_REDIRECT_URI"),
    scope=CONFIG.get("SPOTIFY_SCOPE").split(","),
    cache_path=CONFIG.get("SPOTIFY_CACHE_PATH"),
)
'''
def grab_liked_songs(access_token, db):
    # Initialize Spotipy client with the provided access token
    sp = spotipy.Spotify(auth=access_token)
    
    # Retrieve the user's saved tracks from Spotify, limit to 50 tracks per request
    results = sp.current_user_saved_tracks(limit=50)
    saved_tracks = results['items']
    
    # Fetch all saved tracks by paging through the results until there are no more tracks left
    while results['next']:
        results = sp.next(results)
        saved_tracks.extend(results['items'])

    # Extract relevant information for each saved track
    tracks_info = []
    for item in saved_tracks:
        track_info = {    
            "track_id": item["track"]["id"],
            "track_name": item["track"]["name"],
            "artist_name": item["track"]["artists"][0]["name"],
            "album_name": item["track"]["album"]["name"],
        }
        tracks_info.append(track_info)
    
    # Fetch additional details for each track
    track_details = get_track_details(tracks_info, sp)

    # Define the directory to save the JSON file
    song_data_dir = os.path.join(os.getcwd(), "song_data", sp.current_user()["id"])
    if not os.path.isdir(song_data_dir):
        os.makedirs(song_data_dir)
    file_path = os.path.join(song_data_dir, "liked_songs_track_details.json")
    
    # Save the JSON file into the song_data folder if it doesn't already exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump(track_details, json_file, indent=4)
        
        # Load playlists into the database after saving the JSON file
        load_playlists(db)
'''
# OAuth route for Spotify login
@oauth_router.get("/spotify")
def login_to_spotify(request: Request, response: Response):
    """
    Route for handling Spotify OAuth login.

    Parameters:
        request (Request): The incoming request object.
        response (Response): The outgoing response object.

    Returns:
        RedirectResponse: A redirect response to the specified URL if the code is present in the query parameters.
        RedirectResponse: A redirect response to the Spotify authorization URL if the code is not present.

    This function handles the Spotify OAuth login process. It first checks if the code parameter is present in the query parameters. If it is, it exchanges the code for an access token using the `sp_oauth.get_access_token` function. It then creates a Spotify client using the access token.

    Next, it retrieves or creates a user in the database using the `get_spotify_user` function. If the user does not exist, it creates a new user using the `create_spotify_user` function. It generates a JWT token using the `tokens.create_spotify_token` function.

    After that, it prepares the response data, which includes the JWT token, Spotify ID, and username. It encodes the response data as a query string and constructs a redirect URL. Finally, it returns a redirect response to the specified URL.

    If the code parameter is not present in the query parameters, it prints a message and returns a redirect response to the Spotify authorization URL.

    Note: This function assumes the presence of the `sp_oauth` object and the `get_spotify_user`, `create_spotify_user`, and `tokens.create_spotify_token` functions.
    """

    code = request.query_params.get("code")

    if code:
        # Exchange code for access token
        token = sp_oauth.get_access_token(code)
        sp = Spotify(auth=token["access_token"])
        
        # Get or create user in the database
        user = get_spotify_user(sp.current_user()["id"], request.app.database)
        if user is None:
            user = create_spotify_user(
                sp.current_user()["display_name"],
                sp.current_user()["id"],
                request.app.database,
            )
        # Generate JWT token
        jwt_token = tokens.create_spotify_token(
            token["access_token"], token["expires_at"], token["scope"]
        )        
        
        # Prepare response data
        response_data = {
            "jwt": jwt_token,
            "spotify_id": user["spotify_id"],
            "username": user["username"]  # Include liked songs in the response
        }    
        query_string = urlencode(response_data)
        redirect_url = f"http://localhost:3000/Contact?{query_string}"
        #grab_liked_songs(token['access_token'],request.app.database)

        return RedirectResponse(url=redirect_url)
        
    else:
        print("No token found. Re-authenticating...")
        auth_url = sp_oauth.get_authorize_url()
        response = RedirectResponse(url=auth_url)
        return response