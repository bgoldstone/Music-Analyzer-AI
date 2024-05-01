import React, { useState } from 'react';
import Loading from './Loading'; // Import the Loading component
import '../App.css'
import background from "../dj-background.jpg";

const Contact = () => {
    const [playlist, setPlaylist] = useState(null);
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false); // Add loading state

    const handleInputChange = (event) => {
        setDescription(event.target.value);
    };

    const handleBeginClick = () => {
        // Show loading page
        setLoading(true);
    
        fetch('http://localhost:8000/playlists/generate', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                "description": description,
                "jwt": " ",
                "keywords": " ",
                "mood": " "
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Get all tracks from the response
            const allTracks = data.tracks;
    
    
            // Update playlist
            setPlaylist({ tracks: allTracks });

            // Hide loading page
            setLoading(false);
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide loading page in case of error
            setLoading(false);
        });
    };


    return (
        <div className="login" style={{ 
                  backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', backgroundAttachment: 'fixed', overflowY: 'scroll'}}>
            <header className="App-header">
                <h1 className="header-title">How are you feeling dawg</h1>
                <label className="header-label">You may put a few words or even a few sentences</label>
                <textarea
                    id="moodinput"
                    name="moodinput"
                    value={description}
                    onChange={handleInputChange}
                ></textarea>
                {/* Render Link conditionally based on loading state */}
                {loading ? (
                    <Loading />
                ) : (
                    <div>
                        <button className="Clickable-text" onClick={handleBeginClick}>Generate Playlist</button>
                        {playlist && (
                            <div>
                                <h2>Generated Playlist</h2>
                                {playlist.tracks.map(track => (
                                    <div key={track.track_id}>
                                        <br />
                                        <br />
                                        <p>Song: {track.track_name}</p>
                                        <p>Artist: {track.artist_name}</p>
                                        <br />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </header>
        </div>
    );
};

export default Contact;