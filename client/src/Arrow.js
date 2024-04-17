// src/Arrow.js
import React from 'react';

const Arrow = ({ circle_radius, centerX, centerY, distance, angle_corrected }) => {
    // Correct arrowLength
    const maxarrowLength = 200;
    const arrowLength = Math.min(
        Math.max(
            distance,
            circle_radius
        ),
        maxarrowLength // Maximum length of the arrow
    );


    // console.log("Arrow centerX: ", centerX, "centerY: ", centerY, "arrowLength: ", arrowLength, "angle_corrected: ", angle_corrected, "distance: ", distance)
    const arrowStyle = {
        position: 'absolute',
        transformOrigin: '0% 50%',
        transform: `translate(${circle_radius}px, ${circle_radius - arrowLength/2}px) rotate(${-angle_corrected}deg)`,
        width: `${arrowLength}px`,
        height: `${arrowLength}px`, // Assuming a fixed height for the arrow SVG
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