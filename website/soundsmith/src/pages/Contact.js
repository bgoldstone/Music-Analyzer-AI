import React, { useState } from 'react';
import Loading from './Loading'; // Import the Loading component
import '../App.css'
import background from "../dj-background.jpg";
import {Link} from "react-router-dom"; // Import Outlet and Link from react-router-dom
import PlaylistUpload from './PlaylistUpload';


const Contact = () => {
    // State variables
    const [playlist, setPlaylist] = useState(null); // State to hold the generated playlist
    const [description, setDescription] = useState(''); // State to hold the user's input description
    const [loading, setLoading] = useState(false); // State to manage loading state
    const [playlist_upload, setPlaylistUpload] = useState(false); // State to manage Playlist upload state

    // Function to handle textarea input change
    const handleInputChange = (event) => {
        setDescription(event.target.value);
    };

    // Function to handle "Generate Playlist" button click
    const handleBeginClick = () => {
        // Show loading indicator
        setLoading(true);
        
    
        fetch('http://localhost:8000/playlists/generate', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                "description": description,
                "jwt": " ", // Placeholder for JWT token
                "keywords": " ", // Placeholder for keywords
                "mood": " " // Placeholder for mood
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Extract playlist tracks from the response
            const allTracks = data.tracks;
    
            // Update the playlist state with the fetched tracks
            setPlaylist({ tracks: allTracks });

            // Hide loading indicator after fetching data
            setLoading(false);
             setPlaylistUpload(true)
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide loading indicator in case of error
            setLoading(false);
            setPlaylistUpload(false)
        });

    };

    // JSX rendering
    return (
        <div className="login" style={{ 
                  backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', backgroundAttachment: 'fixed', overflowY: 'scroll'}}>
            <header className="Contact-header">
                <h1 className="header-title">How are you feeling dawg</h1>
                <label className="header-label">You may put a few words or even a few sentences</label>
                {/* Textarea for user input */}
                <textarea
                    id="moodinput"
                    name="moodinput"
                    value={description}
                    onChange={handleInputChange}
                ></textarea>
                {/* Conditionally render loading indicator or button based on loading state */}
                {loading ? (
                    // Display loading component while fetching data
                    <Loading />
                ) : (
                    // Button to trigger playlist generation
                    <div>
                        <button className="Clickable-text" onClick={handleBeginClick}>Generate Playlist</button>
                        {/* Render playlist if it exists */}
                        {playlist && (
                            <div>

                                {/* Iterate over playlist tracks and display them */}
                                {playlist.tracks.map(track => (
                                    <div key={track.track_id}>
                                        <br />
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
                {playlist_upload ? (
                    <PlaylistUpload />
                ) : (
                    <div></div>
                )}
            </header>
        </div>
    );
};

export default Contact;