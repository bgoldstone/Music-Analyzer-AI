from datetime import datetime
from typing import Dict, List, Optional
from load_data import get_async_db_connection, get_db_connection
from auth import hasher

db = get_db_connection()


def get_user(username: str) -> str | None:
    """Get user from database from username asyncrously

    Args:
        username (str): Username

    Returns:
        str: User ID
    """
    return db["users"].find_one({"username": username}).get("_id")


def create_user(username: str, password: str) -> str:
    """Create user in database

    Args:
        username (str): Username
        password (str): Password

    Returns:
        str: User ID
    """
    user = {"username": username, "password": hasher.hash_password(password)}
    user["time"] = datetime.now()
    return db["users"].insert_one(user).inserted_id


def update_user(
    user_id: str, username: Optional[str] = None, password: Optional[str] = None
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
                "$set": {"password": hasher.hash_password(password)},
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
                "password": hasher.hash_password(password),
                "time": datetime.now(),
            }
        },
    )


def delete_user(username: str) -> None:
    """Delete user in database

    Args:
        db (MongoClient): Database
        username (str): Username
    """
    db["users"].delete_one({"username": username})


def get_playlist_by_name(playlist_name: str, user_id: str) -> Dict | None:
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


def get_playlist_by_id(playlist_id: str) -> Dict | None:
    """Searches database for Playlist with Playlist ID.

    Args:
        playlist_id (str): Playlist ID.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    return db["playlists"].find_one({"_id": playlist_id})


def create_playlist(user_id: str, playlist_name: str, tracks: List[str]) -> str:
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
    return db["playlists"].insert_one(playlist).inserted_id


def delete_playlist(playlist_id: str) -> None:
    """Deletes Playlist from the database.

    Args:
        playlist_id (str): Playlist ID.
    """
    db["playlists"].delete_one({"_id": playlist_id})


def update_playlist_by_id(
    playlist_id: str,
    playlist_name: Optional[str] = None,
    tracks: Optional[List[str]] = None,
) -> None:
    """Updates Playlist in the database.

    Args:
        playlist_id (str): Playlist ID.
        playlist_name (Optional[str]): Playlist Name.
        tracks (Optional[List[str]]): Track IDs.

    Returns:
        Nones
    """
    # if playlist_name is None, update only tracks
    if playlist_name is None:
        return db.update_one(
            {"_id": playlist_id}, {"$set": {"tracks": tracks, "time": datetime.now()}}
        )
    # if tracks is None, update only playlist_name
    if tracks is None:
        return db.update_one(
            {"_id": playlist_id},
            {"$set": {"playlist_name": playlist_name, "time": datetime.now()}},
        )
    # if both playlist_name and tracks are not None, update both
    return db.update_one(
        {"_id": playlist_id},
        {
            "$set": {
                "playlist_name": playlist_name,
                "tracks": tracks,
                "time": datetime.now(),
            }
        },
    )


def get_track_by_id(track_id: str) -> Dict | None:
    """Searches database for Track with Track ID.

    Args:
        track_id (str): Track ID.

    Returns:
        Dict: Track Object or None if not found.
    """
    return db["tracks"].find_one({"_id": track_id})


def get_track_by_name_artist(track_name: str, artist_name: str) -> Dict | None:
    """Searches database for Track with Track Name and Artist Name.

    Args:
        track_name (str): Track Name.
        artist_name (str): Artist Name.

    Returns:
        Dict: Track Object or None if not found.
    """
    return db["tracks"].find_one(
        {"track.track_name": track_name, "track.artist_name": artist_name}
    )


def create_track(track: Dict[str, str]) -> str:
    """Creates Track in the database

    Args:
        track (Dict[str, str]): Track

    Returns:
        str: Track ID
    """
    track["time"] = datetime.now()
    return db["tracks"].insert_one(track).inserted_id


def update_track(track_id: str, track: Dict[str, str]) -> None:
    """Updates Track in the database

    Args:
        track_id (str): Track ID
        track (Dict[str, str]): Track
    """
    db["tracks"].update_one({"_id": track_id}, {"$set": track, "time": datetime.now()})


def delete_track(track_id: str) -> None:
    """Deletes Track from the database

    Args:
        track_id (str): Track ID
    """
    db["tracks"].delete_one({"_id": track_id})


# aggregations


def get_playlist_with_tracks(playlist_name: str) -> Dict | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        playlist_name (str): Playlist Name.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    return (
        db["playlists"]
        .aggregate(
            [
                {"$match": {"playlist_name": "songs-for-events"}},
                {
                    "$lookup": {
                        "from": "tracks",
                        "localField": "tracks",
                        "foreignField": "_id",
                        "as": "tracks",
                    }
                },
                {"$project": {"tracks.track": 1, "user_id": 1, "playlist_name": 1}},
            ]
        )
        .next()
    )
