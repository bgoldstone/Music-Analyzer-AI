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

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from auth import tokens
from database.crud import create_spotify_user, create_user, get_spotify_user

CONFIG = dotenv.dotenv_values("spotify_data_retrival/.env")

app = FastAPI()

oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])
sp_oauth = oauth2.SpotifyOAuth(
    CONFIG.get("SPOTIFY_CLIENT_ID"),
    CONFIG.get("SPOTIFY_CLIENT_SECRET"),
    CONFIG.get("SPOTIFY_REDIRECT_URI"),
    scope=CONFIG.get("SPOTIFY_SCOPE").split(","),
    cache_path=CONFIG.get("SPOTIFY_CACHE_PATH"),
)

def grab_liked_songs(access_token):
    sp = spotipy.Spotify(auth=access_token)
    results = sp.current_user_saved_tracks(limit=50)
    saved_tracks = results['items']
    
    while results['next']:
        results = sp.next(results)
        saved_tracks.extend(results['items'])

    tracks_info = []
    for item in saved_tracks:
        track_info = {
            "id": item['track']['id'],
            "name": item['track']['name'],
            "artist": item['track']['artists'][0]['name']
        }
        tracks_info.append(track_info)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

# OAuth route for Spotify login
@oauth_router.get("/spotify")
def login_to_spotify(request: Request, response: Response):
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
        # Grab liked songs for the user
        liked_songs = grab_liked_songs(token["access_token"])
        print(liked_songs)
        # Prepare response data
        response_data = {
            "jwt": jwt_token,
            "spotify_id": user["spotify_id"],
            "username": user["username"],
            "liked_songs": liked_songs  # Include liked songs in the response
        }    
        query_string = urlencode(response_data)
        redirect_url = f"http://localhost:3000/Contact?{query_string}"
        return RedirectResponse(url=redirect_url)
        
    else:
        print("No token found. Re-authenticating...")
        auth_url = sp_oauth.get_authorize_url()
        response = RedirectResponse(url=auth_url)
        return response