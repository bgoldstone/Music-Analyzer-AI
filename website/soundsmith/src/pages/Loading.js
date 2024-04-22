import React from 'react';

const Loading = () => {
    return (
        <div className="Loading">
            <div className="loading-spinner">
                {/* Replace the rotating spinner with the "Crafting..." message */}
                <span className="loading-message">Crafting...</span>
            </div>
        </div>
    );
}

export default Loading;