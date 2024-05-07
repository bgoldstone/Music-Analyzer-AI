import React from 'react';
import {Link} from "react-router-dom"; // Import Outlet and Link from react-router-dom
import '../App.css'


// Define the Loading component
const PlaylistUpload = () => {

    // Function to call the API to ulpoad the playlist to Spotify
    const uploadPlaylist = () => {
        fetch('http://localhost:8000/generate',{})
        

    }

    return (
        // Render the Spotify playlist upload component
        <div>
            <h3>Would you like to add this playlist to your Spotify?</h3>
            <button className="Clickable-text" onClick={uploadPlaylist}>Yes</button>
            <div className="Clickable-text"><Link to="http://localhost:8000/Home">No</Link></div>
        </div>
    );
}

export default {PlaylistUpload}; // Export the Spotify playlist upload component