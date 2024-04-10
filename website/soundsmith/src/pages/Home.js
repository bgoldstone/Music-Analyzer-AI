import logo from '../musicnotelogo.svg';
import '../App.css';
import background from "../dj-background.jpg";
import React from 'react';
import { Outlet, Link } from "react-router-dom";



const Home = () => {
  return (
    <div className="Home" style={{ 
      backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', }}>
        <header className="App-header">
          <h1>Welcome to SoundSmith</h1>
          <img src={logo} className="App-logo" alt="logo" />
          <p>Crafting Melodies</p>
          {handleBeginClick()}
        </header>
    </div>
  );
}

function handleBeginClick() {
  // Add code to handle click event, navigate to next page
  return(
  <div className="Clickable-text"><Link to="/blogs">Click to Begin</Link></div>)
  
}

export default Home;