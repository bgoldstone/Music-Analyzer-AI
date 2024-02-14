from sqlalchemy import ForeignKey, Table, create_engine, Column, Integer, String, Double, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from typing import Any


DB_NAME = 'project_sound.db'
Base = declarative_base()

# Many-to-Many relationship between playlist and tracks
playlist_track = Table(
    'playlist_track',
    Base.metadata,
    Column('playlist_id', Integer,
           ForeignKey('playlists.id')),
    Column('song_id', Integer,
           ForeignKey('tracks.id'))
)

# Define models


class Track(Base):
    """Tracks ORM Model"""
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    spotify_id = Column(String, index=True, unique=True)
    name = Column(String)
    artist = Column(String)
    album = Column(String)
    playlists = relationship(
        'Playlist', secondary=playlist_track, back_populates='tracks')


class TrackDetails(Base):
    """Playlist ORM Model"""
    __tablename__ = 'track_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_track_id = Column(String, ForeignKey(
        'tracks.spotify_id'), nullable=False, index=True)
    acousticness = Column(Double)
    danceability = Column(Double)
    duration = Column(Integer)
    energy = Column(String)
    instrumentalness = Column(Double)
    key = Column(Integer)
    liveness = Column(Double)
    loudness = Column(Double)
    mode = Column(Integer)
    speechiness = Column(Double)
    tempo = Column(Double)
    time_signature = Column(Integer)
    valence = Column(Double)


class Playlist(Base):
    __tablename__ = 'playlists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    tracks = relationship(
        'Track', secondary=playlist_track, back_populates='playlists')


class Lyrics(Base):
    """Lyrics ORM model"""
    __tablename__ = 'lyrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(String, ForeignKey(
        'tracks.spotify_id'), nullable=False, index=True)
    lyrics = Column(Text)


def main():

    engine = create_engine(f'sqlite:///{DB_NAME}')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    session.close()


if __name__ == '__main__':
    main()
