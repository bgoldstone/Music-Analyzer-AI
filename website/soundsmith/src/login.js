import logo from './spotifylogo.svg';
import './spotifylogin.css';
import background from "./otherspotify.jpg";


function App() {
  return (
    <div className="login" style={{ 
      backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', }}>
        <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
          <h1>Sign Into Your Spotify</h1>
          
          <label>Username or Email</label>
          <input type="text" id="username" name="username" />
          <label>Password</label>
          <input type="password" id="password" name="password" />
          <div className="Clickable-text" onClick={handleBeginClick}>Sign In</div>
        </header>
    </div>
  );
}

function handleBeginClick() {
  // Add code to handle click event (e.g., navigate to next page)
  alert('Let sound adventure begin!');
}

export default App;