// src/Circle.js
import React, { useState } from 'react';

const Circle = ({ initialPosition, circle_radius, maxLengthArrow }) => {
    const [position] = useState(initialPosition);
    const [isSelected, setIsSelected] = useState(false);
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [arrowStyle, setArrowStyle] = useState({ display: 'none' });

    const handleCircleClick = (e) => {
        const dx = e.clientX - position.x;
        const dy = position.y - e.clientY;
        const distanceFromCenter = Math.min(Math.sqrt(dx ** 2 + dy ** 2), maxLengthArrow);
        if (distanceFromCenter <= circle_radius) {
            setIsSelected(!isSelected);
            if (!isSelected) {
                setDefaultArrow();
            } else {
                setArrowStyle({ display: 'none' });
            }
        }
    };

    const handleMouseMove = (e) => {
        if (isMouseDown && isSelected) {
            const dx = e.clientX - position.x;
            const dy = position.y - e.clientY;
            const distance = Math.min(
                Math.max(Math.sqrt(dx ** 2 + dy ** 2), circle_radius),
                maxLengthArrow
            );
            const angle = Math.atan2(dy, dx) * (180 / Math.PI);
            const angle_corrected = angle < 0 ? 360 + angle : angle;
            setArrow(position.x, position.y, distance, angle_corrected);
        }
    };

    const setDefaultArrow = () => {
        setArrow(position.x, position.y, 100, 0);
    };

    const setArrow = (centerX, centerY, distance, angle_corrected) => {
        setArrowStyle({
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
        });
    };

    // Set up event listeners for mouse actions
    document.onmousedown = () => setIsMouseDown(true);
    document.onmouseup = () => setIsMouseDown(false);

    return (
        <div onMouseUp={handleCircleClick} onMouseMove={handleMouseMove} style={{
            position: 'relative', width: '100vw', height: '100vh'
        }}>
            <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                backgroundColor: isSelected ? 'red' : 'black',
                position: 'absolute',
                left: `${position.x - circle_radius}px`,
                top: `${position.y - circle_radius}px`,
            }} />
            <div style={arrowStyle} />
        </div>
    );
};

export default Circle;
