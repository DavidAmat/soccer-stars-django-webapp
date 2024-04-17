// src/Arrow.js
import React from 'react';

const Arrow = ({ centerX, centerY, distance, angle_corrected }) => {
    const arrowStyle = {
        position: 'absolute',
        transformOrigin: '0% 50%',
        transform: `translate(${centerX}px, ${centerY - distance / 2}px) rotate(${-angle_corrected}deg)`,
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