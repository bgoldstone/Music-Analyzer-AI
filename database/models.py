from sqlalchemy import ForeignKey, Numeric, Table, create_engine, Column, Integer, String, Double, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


DB_NAME = 'project_sound.db'
Base = declarative_base()

# Many-to-Many relationship between playlist and tracks


class PlaylistTrack(Base):
    __tablename__ = 'playlist_tracks'
    playlist_id = Column(Integer, ForeignKey('playlists.id'), primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), primary_key=True)


# Define models
class Track(Base):
    """Tracks ORM Model"""
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    spotify_id = Column(String, index=True, unique=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    # Track relationship to playlists
    playlists = relationship(
        'Playlist', secondary="playlist_tracks", back_populates='tracks')


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
    # Playlist relationship to tracks
    tracks = relationship(
        'Track', secondary="playlist_tracks", back_populates='playlists')


class Lyrics(Base):
    """Lyrics ORM model"""
    __tablename__ = 'lyrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(String, ForeignKey(
        'tracks.id'), nullable=False, index=True)
    lyrics = Column(Text)


class Analysis(Base):
    """Analysis ORM model"""
    __tablename__ = 'analysis'
    track_id = Column(String, ForeignKey(
        'tracks.id'), primary_key=True, nullable=False, index=True)
    # Emotional Analysis
    happiness = Column(Numeric(10, 2))
    surprise = Column(Numeric(10, 2))
    sadness = Column(Numeric(10, 2))
    # Feelings Analysis
    tension = Column(Numeric(10, 2))
    expressiveness = Column(Numeric(10, 2))
    amusement = Column(Numeric(10, 2))
    attractiveness = Column(Numeric(10, 2))


def main():

    engine = create_engine(f'sqlite:///{DB_NAME}')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    session.close()


if __name__ == '__main__':
    main()
