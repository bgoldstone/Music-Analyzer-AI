from typing import Dict
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from database.crud import (
    get_track,
    create_track,
    delete_track,
    get_track_by_name,
    update_track,
)

from api.models import Track, TrackUpdate

track_router = APIRouter(prefix="/tracks", tags=["tracks"])


@track_router.get(
    "/{track_id}",
    response_description="Get a single track",
)
def get_track_by_id(track_id: str, request: Request) -> Dict:
    track = get_track(track_id, request.app.database)
    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_id} not found",
        )
    track["_id"] = str(track["_id"])
    return track


@track_router.post(
    "/",
    response_description="Create a new track",
)
def create_new_track(track: Track, request: Request) -> Dict:
    track = create_track(jsonable_encoder(track), request.app.database)
    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track could not be created",
        )
    return {"track_id": track}


@track_router.put(
    "/{track_id}",
    response_description="Update a track",
)
def update_track_by_id(track_id: str, track: TrackUpdate, request: Request) -> None:
    track = update_track(track_id, track, request.app.database)

@track_router.get('/{artist}/{track_name}', response_description='Get a single track by artist and track name')
def get_track_by_name_and_artist(artist:str, track_name:str, request:Request) -> Dict:
    track = get_track_by_name(track_name, artist, request.app.database)
    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_name} by {artist} not found",
        )
    track["_id"] = str(track["_id"])
    print(track)
    return track

@track_router.delete(
    "/{track_id}",
    response_description="Delete a track",
)
def delete_track_by_id(track_id: str, request: Request) -> None:
    delete_track(track_id, request.app.database)
