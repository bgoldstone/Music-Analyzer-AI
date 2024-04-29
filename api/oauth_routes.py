import pathlib
import sys
from fastapi import APIRouter, Request, Response, WebSocket, FastAPI, Query
from fastapi.responses import RedirectResponse, JSONResponse
from spotipy import oauth2, Spotify
import dotenv
from urllib.parse import urlencode
import spotipy
import os
import json

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@oauth_router.get("/spotify")
def login_to_spotify(request: Request, response: Response):
    code = request.query_params.get("code")

    if code:
        token = sp_oauth.get_access_token(code)
        sp = Spotify(auth=token["access_token"])
        user = get_spotify_user(sp.current_user()["id"], request.app.database)
        if user is None:
            user = create_spotify_user(
                sp.current_user()["display_name"],
                sp.current_user()["id"],
                request.app.database,
            )
        # print(token)

        jwt_token = tokens.create_spotify_token(
            token["access_token"], token["expires_at"], token["scope"]
        )
        response_data = {
            "jwt": jwt_token,
            "spotify_id": user["spotify_id"],
            "username": user["username"],
        }    
        query_string = urlencode(response_data)
        redirect_url = f"http://localhost:3000/Contact?{query_string}"
        return RedirectResponse(url=redirect_url)
        
    else:
        print("No token found. Re-authenticating...")
        auth_url = sp_oauth.get_authorize_url()
        response = RedirectResponse(url=auth_url)
        return response
    
# New route to retrieve liked songs
@app.get("/liked-songs")
def retrieve_liked_songs(token: str = Query(...)):
    sp = spotipy.Spotify(auth=token)
    
    # Get the first batch of saved tracks
    results = sp.current_user_saved_tracks(limit=50)
    saved_tracks = results['items']
    
    # Continue retrieving tracks until all tracks are fetched
    while results['next']:
        results = sp.next(results)
        saved_tracks.extend(results['items'])

    # Extract track information
    tracks_info = []
    for item in saved_tracks:
        track_info = {
            "id": item['track']['id'],
            "name": item['track']['name'],
            "artist": item['track']['artists'][0]['name']
        }
        tracks_info.append(track_info)

    return tracks_info