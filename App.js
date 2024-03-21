import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Welcome to SoundSmith</h1>
        <p>Crafting Melodies</p>
        <div className="Clickable-text" onClick={handleBeginClick}>Click to Begin</div>
      </header>
    </div>
  );

  function handleBeginClick() {
    // Add code to handle click event (e.g., navigate to next page)
    alert('Let sound adventure begin!');
  }
}

export default App;