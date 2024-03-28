import logo from '../musicnotelogo.svg';
import '../App.css';
import background from "../dj-background.jpg";
import React from 'react';


const Home = () => {
  return (
    <div className="Home" style={{ 
      backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', }}>
        <header className="App-header">
          <h1>Welcome to SoundSmith</h1>
          <img src={logo} className="App-logo" alt="logo" />
          <p>Crafting Melodies</p>
          <div className="Clickable-text" onClick={handleBeginClick}>Click to Begin</div>
        </header>
    </div>
  );
}

function handleBeginClick() {
  // Add code to handle click event (e.g., navigate to next page)
  alert('Let sound adventure begin!');
}

export default Home;