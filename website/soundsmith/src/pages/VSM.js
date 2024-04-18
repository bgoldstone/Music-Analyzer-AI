import React from 'react';
import '../App.css';

const VSM = ({ emotionPredictions }) => {
    return (
        <div className="App-header">
            <h1>Time to Craft Melodies</h1>
            {emotionPredictions && (
                <div>
                    <h2>Emotion Predictions</h2>
                    <pre>{JSON.stringify(emotionPredictions, null, 2)}</pre>
                </div>
            )}
            {/* Change button class to Clickable-text */}
            <button className="Clickable-text" onClick={() => console.log("Crafting melodies...")}>Craft Melodies</button>
        </div>
    );
};

export default VSM;