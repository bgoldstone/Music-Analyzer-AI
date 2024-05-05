import logo from '../musicnotelogo.svg'; // Import the logo image
import '../App.css'; // Import the CSS file
import background from "../dj-background.jpg"; // Import the background image
import React from 'react';
import { Outlet, Link } from "react-router-dom"; // Import Outlet and Link from react-router-dom

// Define the Home component
const Home = () => {
  return (
    // Render the Home component
    <div className="Home-container" style={{ 
      backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', }}>
        {/* Header section */}
        <header className="Home-header">
          <h1>Welcome to SoundSmith</h1> {/* Display the welcome message */}
          <img src={logo} className="Home-logo" alt="logo" /> {/* Display the logo */}
          <p>Crafting Melodies</p> {/* Display the slogan */}
          {handleBeginClick()} {/* Call the handleBeginClick function */}
        </header>
    </div>
  );
}

// Function to handle the "Click to Begin" link click event
function handleBeginClick() {
  // Add code to handle click event, navigate to next page
  return (
    <div className="Clickable-text"><Link to="http://localhost:8000/oauth/spotify">Click to Begin</Link></div> // Render the link
  );
}

export default Home; // Export the Home component