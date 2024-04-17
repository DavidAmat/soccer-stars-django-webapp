// src/App.js
import React, { useState } from 'react';
import Circle from './Circle';

const App = () => {
    const [selectedCircle, setSelectedCircle] = useState(null);
    const configs = [
        { initialPosition: { x: 250, y: 250 }, circle_radius: 50 },
        { initialPosition: { x: 350, y: 350 }, circle_radius: 50 },
        // Add more circle configs here
    ];

    const handleCircleClick = (index) => {
        setSelectedCircle(selectedCircle === index ? null : index);
    };

    return (
        <div>
            {configs.map((config, index) => (
                <Circle
                    key={index}
                    index={index} // Pass the index prop here
                    initialPosition={config.initialPosition}
                    circle_radius={config.circle_radius}
                    isSelected={selectedCircle === index}
                    onCircleClick={() => handleCircleClick(index)}
                />
            ))}
        </div>
    );
};

export default App;