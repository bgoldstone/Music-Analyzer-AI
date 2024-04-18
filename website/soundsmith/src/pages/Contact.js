import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link
import axios from 'axios';

const Contact = () => {
    const [emotionPredictions, setEmotionPredictions] = useState(null);
    const [description, setDescription] = useState('');

    const handleInputChange = (event) => {
        setDescription(event.target.value);
    };

    const handleBeginClick = async () => {
        try {
            const response = await fetch('http://localhost:8000/playlists/generate', {
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
            });

            const data = await response.json();
            setEmotionPredictions(data);

            await new Promise(resolve => setTimeout(resolve, 100));

            if(data)
                window.location.href = '/vsm'

        } catch (error) {
            console.error('Error:', error);
        }
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
                {/* Use Link to navigate to VSM page */}
                <Link to="/vsm" className="Clickable-text" onClick={handleBeginClick}>Generate Playlist</Link>
            </header>
        </div>
    );
};

export default Contact;