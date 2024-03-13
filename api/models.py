from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
from bson import ObjectId


class User(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")
    username: str
    time: datetime

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "username": "ObjectId('test')",
                "time": datetime.now(),
            }
        }


class UserUpdate(BaseModel):
    username: Optional[str] = None


class Playlist(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")
    playlist_name: str
    user_id: ObjectId
    time: datetime
    tracks: List[str]

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "playlist_name": "test",
                "user_id": "ObjectId('test')",
                "time": datetime.now(),
                "tracks": ["ObjectId('test')", "ObjectId('test2')"],
            }
        }


class PlaylistUpdate(BaseModel):
    playlist_name: Optional[str] = None
    tracks: Optional[List[str]] = None


class Track(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    track_name: str
    artist_name: str
    album_name: str
    analysis: Dict
    spotify: Dict
    time: datetime

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "track_name": "test",
                "artist_name": "test",
                "album_name": "test",
                "analysis": {
                    "danceability": 0.393,
                    "energy": 0.588,
                    "key": 9,
                    "loudness": -6.68,
                    "mode": 0,
                    "speechiness": 0.0613,
                    "acousticness": 0.345,
                    "instrumentalness": 0,
                    "liveness": 0.134,
                    "valence": 0.728,
                    "tempo": 203.145,
                    "analysis_url": "https://api.spotify.com/v1/audio-analysis/1234",
                    "duration_ms": 186333,
                    "time_signature": 4,
                },
                "spotify": {
                    "track_id": "1234",
                    "uri": "spotify:track:1234",
                    "track_href": "https://api.spotify.com/v1/tracks/1234",
                },
                "time": datetime.now(),
            }
        }


class TrackUpdate(BaseModel):
    track_name: Optional[str] = None
    artist_name: Optional[str] = None
    album_name: Optional[str] = None
    analysis: Optional[Dict] = None
    spotify: Optional[Dict] = None
