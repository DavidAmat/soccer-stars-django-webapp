// src/CapArrow.js
import React from 'react';

const CapArrow = ({ capRadius, distance, angle }) => {
    // Correct arrowLength
    const maxarrowLength = 200;

    // Arrow length should be at least the capRadius
    // and should not exceed the maxarrowLength
    const arrowLength = Math.round(Math.min(
        Math.max(
            distance,
            capRadius
        ),
        maxarrowLength // Maximum length of the arrow
    ));


    // console.log("Arrow centerX: ", centerX, "centerY: ", centerY, "arrowLength: ", arrowLength, "angle_corrected: ", angle_corrected, "distance: ", distance)
    //console.log("Arrow capRadius: ", capRadius, "arrowLength: ", arrowLength, "angle: ", angle)
    const arrowStyle = {
        position: 'absolute',
        transformOrigin: '0% 50%',
        transform: `translate(${capRadius}px, ${capRadius - arrowLength/2}px) rotate(${-angle}deg)`,
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

export default CapArrow;