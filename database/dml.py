from typing import List
from sqlalchemy import exists
from sqlalchemy.orm import Session
from models import Track, Lyrics, Playlist, TrackDetails, PlaylistTrack


def create_track(session: Session, track: Track):
    """Creates Track in the database

    Args:
        session (Session): Session Object.
        track (Track): Track Object.
    """
    session.add(track)
    session.commit()


def get_track_by_id(session: Session, track_id: str) -> Track | None:
    """Searches database for Track with Track ID.

    Args:
        session (Session): Session Object.
        track_id (str): Spotify Track ID.

    Returns:
        Track: Track Object or None if not found.
    """
    return session.query(Track).filter(Track.spotify_id == track_id).first()


def get_first_track(session: Session, track_name: str) -> Track | None:
    """Gets First Track in the database that matches the track name.

    Args:
        session (Session): Session Object.
        track_name (str): Track Name.

    Returns:
        Track: Track Object or None if not found.
    """
    return session.query(Track).filter(Track.name == track_name).first()


def get_tracks(session: Session, track_name: str) -> List[Track]:
    """Gets all the tracks that match the track name.

    Args:
        session (Session): Session Object.
        track_name (str): Track Name.

    Returns:
        List[Track]: List of Track Objects.
    """
    return session.query(Track).filter(Track.name == track_name).all()


def update_track(session: Session, track: Track):
    """Updates Track in the database.

    Args:
        session (Session): Session Object.
        track (Track): Track Object.
    """
    session.merge(track)
    session.commit()


def delete_track(session: Session, track: Track):
    """Deletes Track from the database.

    Args:
        session (Session): Session Object.
        track (Track): Track Object.
    """
    session.delete(track)
    session.commit()


def create_playlist(session: Session, playlist: Playlist):
    """Creates Playlist in the database

    Args:
        session (Session): Session Object.
        playlist (Playlist): Playlist Object.
    """
    session.add(playlist)
    session.commit()


def get_playlist_by_id(session: Session, playlist_id: int) -> Playlist | None:
    """Searches database for Playlist with Playlist ID.

    Args:
        session (Session): Session Object.
        playlist_id (int): Playlist ID.

    Returns:
        Playlist: Playlist Object or None if not found.
    """
    return session.query(Playlist).filter(Playlist.id == playlist_id).first()


def get_playlist_by_name(session: Session, playlist_name: str) -> Playlist | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        session (Session): Session Object.
        playlist_name (str): Playlist Name.

    Returns:
        Playlist: Playlist Object or None if not found.
    """
    return session.query(Playlist).filter(Playlist.name == playlist_name).first()


def update_playlist(session: Session, playlist: Playlist):
    """Updates Playlist in the database.

    Args:
        session (Session): Session Object.
        playlist (Playlist): Playlist Object.
    """
    session.merge(playlist)
    session.commit()


def delete_playlist(session: Session, playlist: Playlist):
    """Deletes Playlist from the database.

    Args:
        session (Session): Session Object.
        playlist (Playlist): Playlist Object.
    """
    session.delete(playlist)
    session.commit()


def create_lyrics(session: Session, lyrics: Lyrics):
    """Creates Lyrics in the database

    Args:
        session (Session): Session Object.
        lyrics (Lyrics): Lyrics Object.
    """
    session.add(lyrics)
    session.commit()


def get_lyrics_by_track_id(session: Session, track_id: str) -> Lyrics | None:
    """Searches database for Lyrics with Track ID.

    Args:
        session (Session): Session Object.
        track_id (str): Spotify Track ID.

    Returns:
        Lyrics: Lyrics Object or None if not found.
    """
    return session.query(Lyrics).filter(Lyrics.track_id == track_id).first()


def get_lyrics_by_track_name(session: Session, track_name: str) -> Lyrics | None:
    """Searches database for Lyrics with Track Name.

    Args:
        session (Session): Session Object.
        track_name (str): Track Name.

    Returns:
        Lyrics: Lyrics Object or None if not found.
    """
    # gets first matching track id from Tracks table.
    track_id = get_spotify_id_by_track_name(session, track_name)
    if track_id is None:
        return None
    return session.query(Lyrics).filter(Lyrics.track_id == track_id).first()


def update_lyrics(session: Session, lyrics: Lyrics):
    """Updates Lyrics in the database.

    Args:
        session (Session): Session Object.
        lyrics (Lyrics): Lyrics Object.
    """
    session.merge(lyrics)
    session.commit()


def delete_lyrics(session: Session, lyrics: Lyrics):
    """Deletes Lyrics from the database.

    Args:
        session (Session): Session Object.
        lyrics (Lyrics): Lyrics Object.
    """
    session.delete(lyrics)
    session.commit()


def create_track_details(session: Session, track_details: TrackDetails):
    """Creates TrackDetails in the database

    Args:
        session (Session): Session Object.
        track_details (TrackDetails): TrackDetails Object.
    """
    session.add(track_details)
    session.commit()


def get_track_details_by_track_id(session: Session, track_id: str) -> TrackDetails | None:
    """Searches database for TrackDetails with Track ID.

    Args:
        session (Session): Session Object.
        track_id (str): Spotify Track ID.

    Returns:
        TrackDetails: TrackDetails Object or None if not found.
    """
    return session.query(TrackDetails).filter(TrackDetails.track_id == track_id).first()


def get_track_details_by_track_name(session: Session, track_name: str) -> TrackDetails | None:
    """Searches database for TrackDetails with Track Name.

    Args:
        session (Session): Session Object.
        track_name (str): Track Name.

    Returns:
        TrackDetails: TrackDetails Object or None if not found.
    """
    # gets first matching track id from Tracks table.
    track_id = get_spotify_id_by_track_name(session, track_name)
    if not track_id:
        return None
    return session.query(TrackDetails).filter(TrackDetails.spotify_track_id == track_id).first()


def update_track_details(session: Session, track_details: TrackDetails):
    """Updates TrackDetails in the database.

    Args:
        session (Session): Session Object.
        track_details (TrackDetails): TrackDetails Object.
    """
    session.merge(track_details)
    session.commit()


def delete_track_details(session: Session, track_details: TrackDetails):
    """Deletes TrackDetails from the database.

    Args:
        session (Session): Session Object.
        track_details (TrackDetails): TrackDetails Object.
    """
    session.delete(track_details)
    session.commit()


# HELPER FUNCTIONS
def get_spotify_id_by_track_name(session: Session, track_name: str) -> TrackDetails | None:
    """Searches database for TrackDetails with Track Name.

    Args:
        session (Session): Session Object.
        track_name (str): Track Name.

    Returns:
        TrackDetails: TrackDetails Object or None if not found.
    """
    # gets first matching track id from Tracks table.
    track: Track = session.query(Track).filter(
        Track.name == track_name).first()
    if track is None:
        return None
    return track.spotify_id


def is_track_in_playlist(session: Session, playlist_id: int, track_id: str) -> bool:
    """Checks if a track is in a playlist.

    Args:
        session (Session): Session Object.
        playlist_id (int): Playlist Table ID.
        track_id (str): Track Table ID.

    Returns:
        bool: True if track is in playlist, False otherwise.
    """
    playlist: Playlist = get_playlist_by_id(session, playlist_id)
    # if playlist doesn't exist
    if playlist is None:
        return False
    # if track exists
    return session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == playlist_id, PlaylistTrack.track_id == track_id).first() is not None
