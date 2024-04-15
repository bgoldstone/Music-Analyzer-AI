import pathlib
import sys
from fastapi import APIRouter, Request, Response, WebSocket
from fastapi.responses import RedirectResponse
from requests import request
from spotipy import oauth2, Spotify
import dotenv

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
        return {
            "jwt": jwt_token,
            "spotify_id": user["spotify_id"],
            "username": user["username"],
        }
    else:
        print("No token found. Re-authenticating...")
        auth_url = sp_oauth.get_authorize_url()
        response = RedirectResponse(url=auth_url)
        return response
    

