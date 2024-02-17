-- playlists definition

CREATE TABLE playlists (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	PRIMARY KEY (id)
);


-- tracks definition

CREATE TABLE tracks (
	id INTEGER NOT NULL, 
	spotify_id VARCHAR, 
	name VARCHAR, 
	artist VARCHAR, 
	album VARCHAR, 
	PRIMARY KEY (id), 
	UNIQUE (id)
);

CREATE UNIQUE INDEX ix_tracks_spotify_id ON tracks (spotify_id);


-- lyrics definition

CREATE TABLE lyrics (
	id INTEGER NOT NULL, 
	track_id VARCHAR NOT NULL, 
	lyrics TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(track_id) REFERENCES tracks (spotify_id)
);

CREATE INDEX ix_lyrics_track_id ON lyrics (track_id);


-- playlist_track definition

CREATE TABLE playlist_track (
	playlist_id INTEGER, 
	song_id INTEGER, 
	FOREIGN KEY(playlist_id) REFERENCES playlists (id), 
	FOREIGN KEY(song_id) REFERENCES tracks (id)
);


-- track_details definition

CREATE TABLE track_details (
	id INTEGER NOT NULL, 
	spotify_track_id VARCHAR NOT NULL, 
	acousticness DOUBLE, 
	danceability DOUBLE, 
	duration INTEGER, 
	energy VARCHAR, 
	instrumentalness DOUBLE, 
	"key" INTEGER, 
	liveness DOUBLE, 
	loudness DOUBLE, 
	mode INTEGER, 
	speechiness DOUBLE, 
	tempo DOUBLE, 
	time_signature INTEGER, 
	valence DOUBLE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(spotify_track_id) REFERENCES tracks (spotify_id)
);

CREATE INDEX ix_track_details_spotify_track_id ON track_details (spotify_track_id);