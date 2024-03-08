from typing import Any, Dict, List, Optional
from database import crud
from auth import tokens
from database.load_data import get_db_connection

from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import uvicorn

app = FastAPI()

db = get_db_connection()


class User(BaseModel):
    username: str
    password: str


class Playlist(BaseModel):
    playlist_name: str
    token: str
    tracks: List[Any]


class Tracks(BaseModel):
    token: str
    track: Optional[Dict[str, str]]
    id: Optional[str]


# dev credentials: username: 'admin', password: 'soundsmith2024'
@app.post("/auth")
def get_auth_token(user: User, response: Response):
    resp = crud.get_jwt_token(user.username, user.password, db)
    if resp is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Invalid username or password"}
    return resp


@app.post("/playlist/get")
def get_playlist(playlist: Playlist, response: Response):
    validate = validate_request(playlist.token, response)
    if validate is not None:
        return validate
    resp = crud.get_playlist_with_tracks(playlist.playlist_name, db)
    return resp


@app.post("/playlist/create")
def create_playlist(playlist: Playlist, response: Response):
    validate = validate_request(playlist.token, response)
    if validate is not None:
        return validate
    resp = crud.create_playlist(
        playlist.token, playlist.playlist_name, playlist.tracks, db
    )
    return resp


@app.put("/playlist")
def update_playlist(playlist: Playlist, response: Response):
    validate = validate_request(playlist.token, response)
    if validate is not None:
        return validate
    user = tokens.decode_token(playlist.token)
    playlist_to_update = crud.get_playlist_by_name(
        playlist.playlist_name, user["_id"], db
    )
    if playlist_to_update is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Playlist not found"}
    crud.update_playlist(
        playlist_to_update.get("_id"),
        db,
        playlist.playlist_name,
        playlist.tracks,
    )
    return {
        "message": "Playlist updated",
        "_id": str(playlist_to_update.get("_id")),
        "playlist_name": playlist.playlist_name,
    }


@app.delete("/playlist")
def delete_playlist(playlist: Playlist, response: Response):
    validate = validate_request(playlist.token, response)
    if validate is not None:
        return validate
    user = tokens.decode_token(playlist.token)
    playlist_to_delete = crud.get_playlist_by_name(
        playlist.playlist_name, user["_id"], db
    )
    if playlist_to_delete is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Playlist not found"}
    crud.delete_playlist(playlist_to_delete.get("_id"), db)
    return {"message": "Playlist deleted"}


@app.post("/track/create")
def create_track(track: Tracks, response: Response):
    validate = validate_request(track.token, response)
    if validate is not None:
        return validate
    crud.create_track(track.track, db)


@app.post("/track/get")
def get_track(track: Tracks, response: Response):
    validate = validate_request(track.token, response)
    if validate is not None:
        return validate
    if track.id is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Track not found"}
    db_track = crud.get_track_by_id(track.id, db)
    if db_track is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Track not found"}
    return db_track


@app.put("/track")
def update_track(track: Tracks, response: Response):
    validate = validate_request(track.token, response)
    if validate is not None:
        return validate
    crud.update_track(track.id, db, track.track)


@app.delete("/track")
def delete_track(track: Tracks, response: Response):
    validate = validate_request(track.token, response)
    if validate is not None:
        return validate
    crud.delete_track(track.id, db)


# helper functions
def validate_request(token: str, response: Response) -> None:
    if token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    elif not tokens.validate_token(token):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}


def main():
    uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="debug", reload=False)


if __name__ == "__main__":
    main()
