import csv
from io import TextIOWrapper
import os
from re import L
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ddl import Playlist, Track, TrackDetails
from dml import create_track, create_track_details, create_playlist, get_playlist_by_name, get_track_by_id, get_track_details_by_track_id


DB_NAME: str = 'project_sound.db'

SONG_DATA_DIRECTORY: str = os.path.join(os.getcwd(), 'song_data')


def main():

    session = get_db_connection()
    load_playlist_track_details(session)
    close_db_connection(session)


def get_db_connection() -> sessionmaker[Session]:
    """Creates and returns db connection.

    Returns:
        sessionmaker[Session]: Session object
    """
    engine = create_engine(f'sqlite:///{DB_NAME}')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def close_db_connection(session: sessionmaker[Session]):
    """Closes the database connection

    Args:
        session (sessionmaker[Session]): Session object
    """
    session.close()


def load_playlist_track_details(session: Session):
    """Loads the song data into the database.
    Args:
        session (Session): Session Object.
    """
    for folder in os.listdir(SONG_DATA_DIRECTORY):
        for playlist in os.listdir(SONG_DATA_DIRECTORY + '/' + folder):
            playlist_file = open(
                f'{SONG_DATA_DIRECTORY}/{folder}/{playlist}', 'r', encoding="utf-8")

            print(playlist.replace(".csv", ""))
            # if playlist file
            if (playlist.endswith("_ids.csv")):
                playlist_name = playlist.replace(
                    "_ids.csv", "").replace("_", " ")
                read_playlist(session, playlist_file, playlist_name)

            # else song details
            else:
                read_track_details(session, playlist_file)


def read_playlist(session: Session, file: TextIOWrapper, playlist_name: str):
    """Reads a playlist file and creates a playlist object if it does not already exist.
    Args:
        session (Session): Session Object.
        file (TextIOWrapper): Playlist File.
        playlist_name (str): Playlist Name.
    """
    playlist = csv.DictReader(file, delimiter=',')
    playlist_obj = Playlist()
    playlist_obj.name = playlist_name
    playlist_obj.tracks = []
    search_for_playlist = get_playlist_by_name(session, playlist_name)
    if (search_for_playlist != None):
        return
    for item in playlist:
        track = get_track_by_id(session, item['track_id'])
        if (track == None):
            track = Track()
            track.spotify_id = item['track_id']
            track.name = item['track_name']
            track.artist = item['artist_name']
            track.album = item['album_name']
            create_track(session, track)
        playlist_obj.tracks.append(track)

    create_playlist(session, playlist_obj)


def read_track_details(session: Session, file: TextIOWrapper):
    """Reads a track details file and creates a track details object if it does not already exist.

    Args:
        session (Session): Session Object.
        file (TextIOWrapper): Track Details File.
    """
    track_details = csv.DictReader(file, delimiter=',')

    for item in track_details:
        track = get_track_details_by_track_id(session, item['track_id'])
        if (track == None):
            track_detail = TrackDetails()
            track_detail.spotify_track_id = item['track_id']
            track_detail.acousticness = float(item['acousticness'])
            track_detail.danceability = float(item['danceability'])
            track_detail.duration = int(item['duration_ms'])
            track_detail.energy = item['energy']
            track_detail.instrumentalness = float(item['instrumentalness'])
            track_detail.key = int(item['key'])
            track_detail.liveness = float(item['liveness'])
            track_detail.loudness = float(item['loudness'])
            track_detail.mode = int(item['mode'])
            track_detail.speechiness = float(item['speechiness'])
            track_detail.tempo = float(item['tempo'])
            track_detail.time_signature = int(item['time_signature'])
            track_detail.valence = float(item['valence'])

            create_track_details(session, track_detail)


if __name__ == '__main__':
    main()
