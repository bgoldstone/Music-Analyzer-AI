from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from database.crud import (
    create_playlist,
    delete_playlist,
    get_playlist_by_name,
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
def create_new_playlist(playlist: Dict, request: Request) -> Dict:
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
