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
            // Update playlist
            setPlaylist(data.playlist);

            // Hide loading page
            setLoading(false);
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide loading page in case of error
            setLoading(false);
        });
};

    // Function to shuffle array elements randomly
    const shuffleArray = (array) => {
        const shuffledArray = [...array]; // Make a copy of the original array
        
        for (let i = shuffledArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1)); // Pick a random index from 0 to i
            [shuffledArray[i], shuffledArray[j]] = [shuffledArray[j], shuffledArray[i]]; // Swap elements
        }
        
        return shuffledArray;
    };
    
    // Function to select unique tracks while limiting the count
    const selectUniqueTracks = (tracks, count) => {
        const uniqueTracks = [];
        const trackIds = new Set();
    
        for (let track of tracks) {
            if (uniqueTracks.length === count) {
                break;
            }
            if (!trackIds.has(track.track_id)) {
                uniqueTracks.push(track);
                trackIds.add(track.track_id);
            }
        }
    
        return uniqueTracks;
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