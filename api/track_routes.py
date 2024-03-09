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
    update_track,
)

from models import Track, TrackUpdate

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
def create_new_track(track: Track, request: Request):
    track = create_track(jsonable_encoder(track), request.app.database)
    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track could not be created",
        )
    return {"track_id": track}


@track_router.put(
    "/{track_id}",
    response_description="Update a track",
)
def update_track_by_id(track_id: str, track: TrackUpdate, request: Request) -> None:
    track = update_track(track_id, track, request.app.database)


@track_router.delete(
    "/{track_id}",
    response_description="Delete a track",
)
def delete_track_by_id(track_id: str, request: Request) -> None:
    delete_track(track_id, request.app.database)
