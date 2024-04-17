// src/App.js
import React, { useState } from 'react';
import Cap from './Cap';

const Match = () => {
    const capRadius = 50;
    const configs = [
        { capIndex: 0, capCenter: { x: 250, y: 250 }},
        { capIndex: 1, capCenter: { x: 550, y: 250 }},
        { capIndex: 2, capCenter: { x: 550, y: 550 }},
        // Add more circle configs here
    ];

    // State variable for the selected Cap
    const [selectedCap, setSelectedCap] = useState(null);

    // Handle Selection of the Circle (with a click)
    const handleCapClick = (capIndex) => {
        // If you clicked on a Cap that is not the selected one
        // then set it as the selected one
        // if you clicked on the selected Cap, then deselect it
        setSelectedCap(capIndex === selectedCap ? null : capIndex);
    };

    return (
        <div>
            {configs.map((config) => (
                <Cap
                    key={config.capIndex}
                    capIndex={config.capIndex}
                    capCenter={config.capCenter}
                    capRadius={capRadius}
                    isSelected={config.capIndex === selectedCap}
                    onCapClick={() => handleCapClick(config.capIndex)}
                />
            ))}
        </div>
        
        
    );
};

export default Match;