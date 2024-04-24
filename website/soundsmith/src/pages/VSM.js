import React, { useState } from 'react';
import '../App.css';

const VSM = () => {
    const [emotionPredictions, setEmotionPredictions] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleCraftMelodiesClick = () => {
        // Show loading page
        setLoading(true);

        // Fetch data
        fetch('http://localhost:8000/playlists/generate', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                "description": "detailed description of the playlist",
                "jwt": "66284846f6b47bd496d9598b",
                "keywords": "list of keywords",
                "mood": "Happy"
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            // Update emotion predictions
            setEmotionPredictions(data);

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
        <div className="App-header">
            <h1>Time to Craft Melodies</h1>
            <button className="Clickable-text" onClick={handleCraftMelodiesClick}>Craft Melodies</button>
            {loading && <p>Loading...</p>}
            {emotionPredictions && (
                <div>
                    <h2>Emotion Predictions</h2>
                    {emotionPredictions.tracks.map(track => (
                        <div key={track.track_id}>
                            <p>Track Name: {track.track_name}</p>
                            <p>Artist Name: {track.artist_name}</p>
                            <br />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default VSM;