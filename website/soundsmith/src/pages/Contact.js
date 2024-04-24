import React, { useState } from 'react';
import Loading from './Loading'; // Import the Loading component
import VSM from './VSM';
const Contact = () => {
    const [emotionPredictions, setEmotionPredictions] = useState(null);
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
                "jwt": "66173c89b970969d7d8d5524",
                "keywords": "list of keywords",
                "mood": " "
            })
        })
        .then(response => {
            if (response.ok) {
                console.log('POST /playlists/generate HTTP/1.1', response.status);
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            // Update emotion predictions
            setEmotionPredictions(data);

            // Simulate delay for 2 seconds before navigating to VSM.js
            setTimeout(() => {
                setLoading(false);
                window.location.href = '/vsm';
            }, 2000);
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide loading page in case of error
            setLoading(false);
        });
    };

    return (
        <div className="login">
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
                    <button className="Clickable-text" onClick={handleBeginClick}>Generate Playlist</button>
                )}
            </header>
        </div>
    );
};

export default Contact;