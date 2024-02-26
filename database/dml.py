from typing import List
from sqlalchemy import exists
from sqlalchemy.orm import Session
from models import Analysis, EmotionalQuantitation, Track, Lyrics, Playlist, TrackDetails, PlaylistTrack, User
from auth.hasher import hash_password, verify_password


def create_track(session: Session, track: Track):
    """Creates Track in the database

    Args:
        session (Session): Session Object.
        track (Track): Track Object.
    """
    if get_track_by_spotify_id(session, track.spotify_id) is not None:
        return
    session.add(track)
    session.commit()


def get_track_by_spotify_id(session: Session, spotify_id: str) -> Track | None:
    """Searches database for Track with Spotify ID.

    Args:
        session (Session): Session Object.
        spotify_id (str): Spotify ID.

    Returns:
        Track: Track Object or None if not found.
    """
    return session.query(Track).filter(Track.spotify_id == spotify_id).first()


def get_track_by_id(session: Session, track_id: str) -> Track | None:
    """Searches database for Track with Track ID.

    Args:
        session (Session): Session Object.
        track_id (str): track id.

    Returns:
        Track: Track Object or None if not found.
    """
    return session.query(Track).filter(Track.id == track_id).first()


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
    if get_track_by_spotify_id(session, track.spotify_id) is None:
        return create_track(session, track)
    session.merge(track)
    session.commit()


def delete_track(session: Session, track: Track):
    """Deletes Track from the database.

    Args:
        session (Session): Session Object.
        track (Track): Track Object.
    """
    if get_track_by_spotify_id(session, track.spotify_id) is None:
        return
    session.delete(track)
    session.commit()


def create_playlist(session: Session, playlist: Playlist):
    """Creates Playlist in the database

    Args:
        session (Session): Session Object.
        playlist (Playlist): Playlist Object.
    """
    if get_playlist_by_name(session, playlist.name, playlist.owner) is not None:
        return
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


def get_playlist_by_name(session: Session, playlist_name: str, user_id: int) -> Playlist | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        session (Session): Session Object.
        playlist_name (str): Playlist Name.
        user_id (int): User ID.

    Returns:
        Playlist: Playlist Object or None if not found.
    """
    return session.query(Playlist).filter(Playlist.name == playlist_name, Playlist.user_id == user_id).first()


def update_playlist(session: Session, playlist: Playlist):
    """Updates Playlist in the database.

    Args:
        session (Session): Session Object.
        playlist (Playlist): Playlist Object.
    """
    if get_playlist_by_id(session, playlist.id) is None:
        return create_playlist(session, playlist)
    session.merge(playlist)
    session.commit()


def delete_playlist(session: Session, playlist: Playlist):
    """Deletes Playlist from the database.

    Args:
        session (Session): Session Object.
        playlist (Playlist): Playlist Object.
    """
    if get_playlist_by_id(session, playlist.id) is None:
        return
    session.delete(playlist)
    session.commit()


def create_lyrics(session: Session, lyrics: Lyrics):
    """Creates Lyrics in the database

    Args:
        session (Session): Session Object.
        lyrics (Lyrics): Lyrics Object.
    """
    if get_lyrics_by_track_id(session, lyrics.track_id) is not None:
        return
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
    if get_track_details_by_track_id(session, track_details.track_id) is not None:
        return
    if get_track_by_id(session, track_details.track_id) is not None:
        return
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


def create_user(session: Session, user: User) -> bool:
    """Creates User in the database

    Args:
        session (Session): Session Object.
        user (User): User Object.

    Returns:
        bool: True if successful, False if user already exists.
    """
    if session.query(User).filter(
            User.username == user.username).first() is not None:
        return False
    session.add(user)
    session.commit()
    return True


def get_user_by_id(session: Session, user_id: int) -> User | None:
    """Searches database for User with User ID.

    Args:
        session (Session): Session Object.
        user_id (int): User ID.

    Returns:
        User: User Object or None if not found.
    """
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_name(session: Session, username: str) -> User | None:
    """Searches database for User with User Name.

    Args:
        session (Session): Session Object.
        user_name (str): User Name.

    Returns:
        User: User Object or None if not found.
    """
    return session.query(User).filter(User.username == username).first()


def update_user_password(session: Session, password: str, username: str):
    """Updates User Password in the database.

    Args:
        session (Session): Session Object.
        password (str): Password.
        user (User): User Object.
    """
    user = get_user_by_name(session, username)
    user.password = hash_password(password)
    session.merge(user)
    session.commit()


def verify_user(session: Session, username: str, password: str) -> bool:
    user = get_user_by_name(session, username)
    if user is None:
        return False
    return verify_password(password, user.password)


def create_analysis(session: Session, analysis: Analysis) -> None:
    """Creates Analysis in the database
    Args:
        session (Session): Session Object.
        analysis (Analysis): Analysis Object.

    Returns:
        None
    """
    if get_analysis(session, analysis.track_id) is not None:
        return
    session.add(analysis)
    session.commit()


def update_analysis(session: Session, analysis: Analysis) -> None:
    """Updates Analysis in the database
    Args:
        session (Session): Session Object.
        analysis (Analysis): Analysis Object.
    Returns:
        None
    """
    if get_analysis(session, analysis.track_id) is None:
        return
    session.merge(analysis)
    session.commit()


def get_analysis(session: Session, track_id: str) -> Analysis | None:
    """Searches database for Analysis with Track ID.
    Args:
        session (Session): Session Object.
        track_id (str): Track ID.
    Returns:
        Analysis: Analysis Object or None if not found.
    """
    return session.query(Analysis).filter(Analysis.track_id == track_id).first()


def delete_analysis(session: Session, analysis: Analysis) -> None:
    """Deletes Analysis in the database
    Args:
        session (Session): Session Object.
        analysis (Analysis): Analysis Object.
    Returns:
        None
    """
    if get_analysis(session, analysis.track_id) is None:
        return
    session.delete(analysis)
    session.commit()


def create_emotional_quantitation(session: Session, quantitation: EmotionalQuantitation) -> None:
    """Creates Emotional Quantitation in the database
    Args:
        session (Session): Session Object.
        quantitation (Quantitation): Quantitation Object.
    Returns:
        None
    """
    if get_emotional_quantitation(session, quantitation.track_id) is not None:
        return
    session.add(quantitation)
    session.commit()


def update_emotional_quantitation(session: Session, quantitation: EmotionalQuantitation) -> None:
    """Updates Quantitation in the database
    Args:
        session (Session): Session Object.
        quantitation (Quantitation): Quantitation Object.
    Returns:
        None
    """
    if get_emotional_quantitation(session, quantitation.track_id) is None:
        create_analysis(session, quantitation)
        return
    session.merge(quantitation)
    session.commit()


def get_emotional_quantitation(session: Session, track_id: str) -> EmotionalQuantitation | None:
    """Searches database for Quantitation with Track ID.
    Args:
        session (Session): Session Object.
        track_id (str): Track ID.
    Returns:
        Quantitation: Quantitation Object or None if not found.
    """
    return session.query(EmotionalQuantitation).filter(EmotionalQuantitation.track_id == track_id).first()


def delete_emotional_quantitation(session: Session, quantitation: EmotionalQuantitation) -> None:
    """Deletes Quantitation in the database
    Args:
        session (Session): Session Object.
        quantitation (Quantitation): Quantitation Object.
    Returns:
        None
    """
    if get_emotional_quantitation(session, quantitation.track_id) is None:
        return
    session.delete(quantitation)
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
