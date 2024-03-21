import pathlib
import sys
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from requests import request
from spotipy import oauth2, Spotify
import dotenv

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from auth import tokens

CONFIG = dotenv.dotenv_values("spotify_data_retrival/.env")

oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])
sp_oauth = oauth2.SpotifyOAuth(
    CONFIG.get("SPOTIFY_CLIENT_ID"),
    CONFIG.get("SPOTIFY_CLIENT_SECRET"),
    CONFIG.get("SPOTIFY_REDIRECT_URI"),
    scope=CONFIG.get("SPOTIFY_SCOPE").split(","),
    cache_path=CONFIG.get("SPOTIFY_CACHE_PATH"),
)


@oauth_router.get("/spotify")
def login_to_spotify(request: Request, response: Response):
    code = request.query_params.get("code")

    if code:
        token = sp_oauth.get_access_token(code)
        sp = Spotify(auth=token["access_token"])
        sp.current_user()
        print(sp.current_user())
        return tokens.create_token(token["access_token"])
    else:
        print("No token found. Re-authenticating...")
        auth_url = sp_oauth.get_authorize_url()
        response = RedirectResponse(url=auth_url)
        return response
