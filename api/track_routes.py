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
    """
    Get a single track by its ID.

    Args:
        track_id (str): The ID of the track to retrieve.
        request (Request): The request object containing the application database.

    Returns:
        Dict: The track with the specified ID, including the "_id" field converted to a string.

    Raises:
        HTTPException: If the track with the specified ID is not found.
    """
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
    """
    Create a new track.

    Args:
        track (Track): The track object to be created.
        request (Request): The request object containing the application database.

    Returns:
        Dict: A dictionary containing the created track's ID.
    """
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
    """
    Update a track by its ID.

    Args:
        track_id (str): The ID of the track to be updated.
        track (TrackUpdate): The updated track object.
        request (Request): The request object containing the application database.

    Returns:
        None: This function does not return anything.
    """
    track = update_track(track_id, track, request.app.database)

@track_router.get('/{artist}/{track_name}', response_description='Get a single track by artist and track name')
def get_track_by_name_and_artist(artist:str, track_name:str, request:Request) -> Dict:
    """
    Get a single track by artist and track name.

    Args:
        artist (str): The name of the artist.
        track_name (str): The name of the track.
        request (Request): The request object containing the application database.

    Returns:
        Dict: The track with the specified artist and track name, including the "_id" field converted to a string.

    Raises:
        HTTPException: If the track with the specified artist and track name is not found.
    """
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
    """
    Delete a track by its ID.

    Args:
        track_id (str): The ID of the track to delete.
        request (Request): The request object containing the application database.

    Returns:
        None
    """
    delete_track(track_id, request.app.database)
