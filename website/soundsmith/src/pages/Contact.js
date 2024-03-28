import '../App.css';
import background from "../dj-background.jpg";
import React from 'react';
               

const Contact = () => {
	return <div className="login" style={{ 
    backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', }}>
      <header className="App-header">
        <h1 className="header-title">How are you feeling dawg</h1> 
        <label className="header-label">You may put a few words or even a few sentences</label> 
        <textarea id="moodinput" name="moodinput"></textarea>
        <div className="Clickable-text" onClick={handleBeginClick}>Sign In</div>
      </header>
    </div>
  };

  function handleBeginClick() {
    // Add code to handle click event (e.g., navigate to next page)
    alert('Let sound adventure begin!');
  }
  
  
  export default Contact;