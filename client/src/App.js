// src/App.js
import React, { useState, useEffect } from 'react';
import Circle from './Circle';
import useMotionCircle from './hooks/useMotionCircle';
import './global.css'; // Import the global styles


const App = () => {
    const [selectedCircle, setSelectedCircle] = useState(null);
    const configs = [
        { initialPosition: { x: 250, y: 550 }, circle_radius: 50 },
        { initialPosition: { x: 350, y: 850 }, circle_radius: 50 },
        // Add more circle configs here
    ];

    // --------------------------------------------
    // Submitting motion
    // --------------------------------------------
    const calculateMotion = (circleIndex, distance, angle_corrected) => {
        // console.log('Calculating motion for circle at index', circleIndex, 'with distance', distance, 'and angle', angle_corrected);
        const motion = {};
        let currentDistance = distance;
        let timestep = 1;
    
        while (currentDistance >= 1) {
            const newPosition = calculateNewPosition(configs[circleIndex].initialPosition, currentDistance, angle_corrected);
            if (!motion[timestep]) {
                motion[timestep] = [];
            }
            motion[timestep].push({ index: circleIndex, newPosition });
            console.log('calculateMotion: [timestep]:', timestep, '[circleIndex]:', circleIndex, '[newPosition]:', newPosition);
    
            currentDistance /= 2;
            timestep += 1;
        }
    
        return motion;
    };

    const calculateNewPosition = (initialPosition, distance, angle) => {
        const angleInRadians = angle * (Math.PI / 180);
        const x = Math.round(initialPosition.x + distance * Math.cos(angleInRadians));
        const y = Math.round(initialPosition.y - distance * Math.sin(angleInRadians));
        return { x, y };
    };

    // --------------------------------------------
    // --------------------------------------------

    // --------------------------------------------
    // handle the motion trigger
    // --------------------------------------------
    // Function to handle the motion trigger
    const handleMotionTrigger = (index, distance, angle_corrected) => {
    // Calculate the motion
    const newMotion = calculateMotion(index, distance, angle_corrected);

    // --------------------------------------------
    // --------------------------------------------
};

    // Use calculateMotion to get the motion object
    const motion = calculateMotion(/* Pass the required parameters here */);

    const positions = useMotionCircle(configs, motion, 0.5);

    const handleCircleClick = (index) => {
        setSelectedCircle(selectedCircle === index ? null : index);
    };

    return (
        <div id="root">
            <div className="background"></div>
            <div className="game-container">
                {positions.map((position, index) => (
                    <Circle
                        key={index}
                        index={index} // Pass the index prop here
                        initialPosition={position}
                        circle_radius={configs[index].circle_radius}
                        isSelected={selectedCircle === index}
                        onCircleClick={() => handleCircleClick(index)}
                        triggerMotion={handleMotionTrigger} // Pass calculateMotion here
                    />
                ))}
            </div>
        </div>
    );
};

export default App;