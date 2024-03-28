import '../App.css';
import logo from '../gears-spinner.svg';
import background from "../dj-background.jpg";
import React from 'react';
           

const Loading = () => {
	return (
		<div className="Loading" style={{
			backgroundImage: `url(${background})`, backgroundPosition: 'center', backgroundSize: 'cover', backgroundRepeat: 'no-repeat', width: '100vw', height: '100vh', }}>
				<header className="Loading-screen">
					<h1>Crafting...</h1>
					<img src={logo} className="loading-logo" alt="load" />
				</header>
		</div>
	)
}
	
	

export default Loading;