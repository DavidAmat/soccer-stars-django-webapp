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

    // State variable for the current configs
    const [currentConfigs, setCurrentConfigs] = useState(configs);

    // State variable for the selected Cap
    const [selectedCap, setSelectedCap] = useState(null);

    // Handle Selection of the Circle (with a click)
    const handleCapClick = (capIndex) => {
        // If you clicked on a Cap that is not the selected one
        // then set it as the selected one
        // if you clicked on the selected Cap, then deselect it
        setSelectedCap(capIndex === selectedCap ? null : capIndex);
    };

    // Handle Cap Submit
    const handleCapSubmit = (capIndex, distance, angle) => {
        const payload = {
            capRadius: capRadius,
            configs: configs,
            arrow: {
                capIndex: capIndex,
                distance: distance,
                angle: angle
            },
        };
        console.log("Payload: ", payload);
        // Call the function to get the motion data
        const motionData = getMotionData();
        //console.log("Motion Data: ", motionData);
        
        // Iterate over the motion data
        motionData.motion.forEach((item, index) => {
            // Delay the execution of the next step
            setTimeout(() => {
                // Update currentConfigs with the configs from the current item
                setCurrentConfigs(item.configs);
            }, index * 100); // Delay by 1 second for each item
        });
    };

    // Function to return the hard-coded motion data
    const getMotionData = () => {
        return {
            motion: [
                {
                    t: 1,
                    configs: [
                        { capIndex: 0, capCenter: { x: 250, y: 250 }},
                        { capIndex: 1, capCenter: { x: 550, y: 250 }},
                        { capIndex: 2, capCenter: { x: 550, y: 550 }},
                    ],
                },
                {
                    t: 2,
                    configs: [
                        { capIndex: 0, capCenter: { x: 270, y: 250 }},
                        { capIndex: 1, capCenter: { x: 550, y: 250 }},
                        { capIndex: 2, capCenter: { x: 550, y: 550 }},
                    ],
                },
                {
                    t: 3,
                    configs: [
                        { capIndex: 0, capCenter: { x: 280, y: 250 }},
                        { capIndex: 1, capCenter: { x: 550, y: 250 }},
                        { capIndex: 2, capCenter: { x: 550, y: 550 }},
                    ],
                },
                {
                    t: 4,
                    configs: [
                        { capIndex: 0, capCenter: { x: 290, y: 250 }},
                        { capIndex: 1, capCenter: { x: 550, y: 250 }},
                        { capIndex: 2, capCenter: { x: 550, y: 550 }},
                    ],
                },
            ]
        };
    };

    return (
        <div>
            {currentConfigs.map((config) => (
                <Cap
                    key={config.capIndex}
                    capIndex={config.capIndex}
                    capCenter={config.capCenter}
                    capRadius={capRadius}
                    isSelected={config.capIndex === selectedCap}
                    onCapClick={() => handleCapClick(config.capIndex)}
                    onCapSubmit={handleCapSubmit} // Pass the new function here
                />
            ))}
        </div>
        
        
    );
};

export default Match;