import React from 'react';

// Define the Loading component
const Loading = () => {
    return (
        // Render the Loading component
        <div className="Loading">
            <div className="loading">
                {/* Display the "Crafting..." message instead of the rotating spinner */}
                <span className="loading-message">Crafting...</span>
            </div>
        </div>
    );
}

export default Loading; // Export the Loading component