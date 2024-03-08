from datetime import datetime
from os import path
from typing import Dict, List, Optional
import sys
import pathlib

from pymongo import MongoClient

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from auth.hasher import hash_password, verify_password
from auth.tokens import create_token
from database.load_data import get_db_connection

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"


def get_jwt_token(username: str, password: str, db: MongoClient) -> str | None:
    """Get user from database from username asyncrously

    Args:
        username (str): Username

    Returns:
        str: User ID
    """
    user = get_user(username, db)
    if user is None:
        return None
    if not verify_password(password, user["password"]):
        return None
    return create_token(user["username"])


def get_user(username: str, db: MongoClient) -> Dict | None:
    """Get user from database from username asyncrously

    Args:
        username (str): Username

    Returns:
        str: User ID
    """
    return db["users"].find_one({"username": username})


def create_user(username: str, password: str, db: MongoClient) -> str:
    """Create user in database

    Args:
        username (str): Username
        password (str): Password

    Returns:
        str: User ID
    """
    user = {"username": username, "password": hash_password(password)}
    user["time"] = datetime.now()
    return db["users"].insert_one(user).inserted_id


def update_user(
    user_id: str,
    db: MongoClient,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """Update user in database

    Args:
        user_id (str): User ID
        username (Optional[str]): Username
        password (Optional[str]): Password
    """
    if username is None:
        db["users"].update_one(
            {"_id": user_id},
            {
                "$set": {"password": hash_password(password)},
                "time": datetime.now(),
            },
        )
        return
    if password is None:
        db["users"].update_one(
            {"_id": user_id}, {"$set": {"username": username, "time": datetime.now()}}
        )
        return
    db["users"].update_one(
        {"_id": user_id},
        {
            "$set": {
                "username": username,
                "password": hash_password(password),
                "time": datetime.now(),
            }
        },
    )


def delete_user(username: str, db: MongoClient) -> None:
    """Delete user in database

    Args:
        db (MongoClient): Database
        username (str): Username
    """
    db["users"].delete_one({"username": username})


def verify_user(username: str, password: str, db: MongoClient) -> bool:
    user = db["users"].find_one({"username": username})
    if user is None:
        return False
    return verify_password(password, user["password"])


def get_playlist_by_name(
    playlist_name: str, user_id: str, db: MongoClient
) -> Dict | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        playlist_name (str): Playlist Name.
        user_id (str): User ID.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    return db["playlists"].find_one(
        {"playlist_name": playlist_name, "user_id": user_id}
    )


def get_playlist_by_id(playlist_id: str, db: MongoClient) -> Dict | None:
    """Searches database for Playlist with Playlist ID.

    Args:
        playlist_id (str): Playlist ID.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    return db["playlists"].find_one({"_id": playlist_id})


def create_playlist(
    user_id: str, playlist_name: str, tracks: List[str], db: MongoClient
) -> str:
    """Create playlist in database

    Args:
        user_id (str): User ID
        playlist_name (str): Playlist Name
        tracks (List[str]): Track IDs

    Returns:
        str: Playlist ID
    """
    playlist = {"playlist_name": playlist_name, "user_id": user_id, "tracks": tracks}
    playlist["time"] = datetime.now()
    return {"_id": str(db["playlists"].insert_one(playlist).inserted_id)}


def delete_playlist(playlist_id: str, db: MongoClient) -> None:
    """Deletes Playlist from the database.

    Args:
        playlist_id (str): Playlist ID.
    """
    db["playlists"].delete_one({"_id": playlist_id})


def update_playlist(
    db: MongoClient,
    tracks: List[str],
    playlist_id: Optional[str] = None,
    playlist_name: Optional[str] = None,
) -> Dict[str, str] | None:
    """Updates Playlist in the database.

    Args:
        db (MongoClient): Database
        tracks (List[str]): Track IDs
        playlist_id (Optional[str]): Playlist ID
        playlist_name (Optional[str]): Playlist Name

    Returns:
        Dict[str, str]: Message and Playlist ID/Name
    """
    # if playlist_name is None, update only tracks
    if playlist_name is None:
        db.update_one(
            {"_id": playlist_id}, {"$set": {"tracks": tracks, "time": datetime.now()}}
        )
        return {"message": "Playlist updated", "_id": playlist_id}
    elif playlist_id is None:
        return None
    db.update_one(
        {"_id": playlist_id},
        {
            "$set": {
                "playlist_name": playlist_name,
                "tracks": tracks,
                "time": datetime.now(),
            }
        },
    )
    return {"message": "Playlist updated", "playlist_name": playlist_name}


def get_track_by_id(track_id: str, db: MongoClient) -> Dict | None:
    """Searches database for Track with Track ID.

    Args:
        track_id (str): Track ID.

    Returns:
        Dict: Track Object or None if not found.
    """
    query = db["tracks"].find_one({"_id": track_id})
    query["_id"] = str(query["_id"])
    return query


def get_track_by_name_artist(
    track_name: str, artist_name: str, db: MongoClient
) -> Dict | None:
    """Searches database for Track with Track Name and Artist Name.

    Args:
        track_name (str): Track Name.
        artist_name (str): Artist Name.

    Returns:
        Dict: Track Object or None if not found.
    """
    query = db["tracks"].find_one(
        {"track.track_name": track_name, "track.artist_name": artist_name}
    )
    query["_id"] = str(query["_id"])
    return query


def create_track(track: Dict[str, str], db: MongoClient) -> Dict[str, str]:
    """Creates Track in the database

    Args:
        track (Dict[str, str]): Track

    Returns:
        str: Track ID
    """
    track["time"] = datetime.now()
    return {"_id": str(db["tracks"].insert_one(track).inserted_id)}


def update_track(track_id: str, track: Dict[str, str], db: MongoClient) -> None:
    """Updates Track in the database

    Args:
        track_id (str): Track ID
        track (Dict[str, str]): Track
    """
    db["tracks"].update_one({"_id": track_id}, {"$set": track, "time": datetime.now()})


def delete_track(track_id: str, db: MongoClient) -> None:
    """Deletes Track from the database

    Args:
        track_id (str): Track ID
    """
    db["tracks"].delete_one({"_id": track_id})


# aggregations


def get_playlist_with_tracks(playlist_name: str, db: MongoClient) -> Dict | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        playlist_name (str): Playlist Name.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    query = (
        db["playlists"]
        .aggregate(
            [
                {"$match": {"playlist_name": f"{playlist_name}"}},
                {
                    "$lookup": {
                        "from": "tracks",
                        "localField": "tracks",
                        "foreignField": "_id",
                        "as": "linkedTracks",
                    }
                },
                {
                    "$set": {
                        "tracks": {
                            "$map": {
                                "input": "$tracks",
                                "as": "t",
                                "in": {
                                    "$first": {
                                        "$filter": {
                                            "input": "$linkedTracks",
                                            "cond": {"$eq": ["$$t", "$$this._id"]},
                                        }
                                    }
                                },
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "tracks.track_name": 1,
                        "tracks.artist_name": 1,
                        "tracks.album_name": 1,
                        "tracks.spotify": 1,
                        "user_id": 1,
                        "playlist_name": 1,
                    }
                },
            ]
        )
        .next()
    )
    query["_id"] = str(query["_id"])
    query["user_id"] = str(query["user_id"])
    return query
