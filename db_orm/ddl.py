from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Double, Text
from sqlalchemy.orm import sessionmaker, declarative_base

DB_NAME = 'project_sound.db'

Base = declarative_base()
# Define models


class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    spotify_id = Column(String, index=True, unique=True)
    name = Column(String)
    artist = Column(String)
    album = Column(String)


class Playlist(Base):
    __tablename__ = 'playlists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    spotify_track_id = Column(String, ForeignKey(
        'tracks.spotify_id'), nullable=False, index=True)
    accousticness = Column(Double)
    dancability = Column(Double)
    duration = Column(Integer)
    engery = Column(String)
    instrumentalness = Column(Double)
    key = Column(Integer)
    liveness = Column(Double)
    loudness = Column(Double)
    mode = Column(Integer)
    speechiness = Column(Double)
    tempo = Column(Double)
    time_signature = Column(Integer)
    valence = Column(Double)


class lyrics(Base):
    __tablename__ = 'lyrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(String, ForeignKey(
        'tracks.spotify_id'), nullable=False, index=True)
    lyrics = Column(Text)


engine = create_engine(f'sqlite:///{DB_NAME}')
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


session.close()
