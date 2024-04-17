// src/Arrow.js
import React from 'react';

const Arrow = ({ circle_radius, centerX, centerY, distance, angle_corrected }) => {
    console.log("Arrow centerX: ", centerX, "centerY: ", centerY, "distance: ", distance, "angle_corrected: ", angle_corrected)
    const arrowStyle = {
        position: 'absolute',
        transformOrigin: '0% 50%',
        transform: `translate(50px, ${circle_radius - distance/2}px) rotate(${-angle_corrected}deg)`,
        width: `${distance}px`,
        height: `${distance}px`, // Assuming a fixed height for the arrow SVG
        pointerEvents: 'none',
        display: 'block',
        backgroundImage: 'url("/icons/arrow.svg")',
        backgroundSize: 'contain',
        backgroundRepeat: 'no-repeat',
    };

    return (
        <div style={arrowStyle} />
    );
};

export default Arrow;