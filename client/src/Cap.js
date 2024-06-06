// src/Cap.js
import React, { useState, useEffect, useRef } from 'react';
import Arrow from './Arrow';

const Cap = ({ initialPosition, cap_radius, isSelected, onCapClick, index, triggerMotion, showIndex }) => {
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [distance, setDistance] = useState(100); // Default distance
    const [angle_corrected, setAngleCorrected] = useState(0); // Default angle
    const capRef = useRef(null); // Reference to the cap div

    // Determine background image based on cap index
    const getBackgroundImage = () => {
        if (index === 10) {
            return 'url("/icons/ball.svg")';
        } else if (index >= 5 && index <= 9) {
            return 'url("/icons/bmw.svg")';
        } else if (index >= 0 && index <= 4) {
            return 'url("/icons/skoda.svg")';
        } else {
            return 'none'; // Default background in case of unexpected index
        }
    };

    const capStyle = {
        width: `${cap_radius * 2}px`,
        height: `${cap_radius * 2}px`,
        position: 'absolute',
        left: `${initialPosition.x - cap_radius}px`,
        top: `${initialPosition.y - cap_radius}px`,
        backgroundImage: getBackgroundImage(),
        backgroundSize: '100% 100%',
        backgroundRepeat: 'no-repeat',
        cursor: 'pointer'
    };

    const indexStyle = {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        color: 'black',
        fontWeight: 'bold',
        fontSize: '26px',
        fontFamily: 'Montserrat, Arial, sans-serif',
        pointerEvents: 'none', // Ensures the number does not interfere with clicking
        userSelect: 'none', // Prevents text selection
    };

    const centerX = initialPosition.x;
    const centerY = initialPosition.y;

    const handleCapClick = (e) => {
        const dx = e.clientX - centerX;
        const dy = centerY - e.clientY;
        const distanceFromCenter = Math.sqrt(dx ** 2 + dy ** 2);
        if (distanceFromCenter <= cap_radius) {
            onCapClick();
        }
    };

    useEffect(() => {
        if (isSelected) {
            setIsMouseDown(false);
        }
    }, [isSelected]);

    useEffect(() => {
        document.onmouseup = () => setIsMouseDown(false);

        const handleMouseMove = (e) => {
            if (isMouseDown && isSelected) {
                const dx = e.clientX - centerX;
                const dy = centerY - e.clientY;
                const distance = Math.round(Math.sqrt(dx ** 2 + dy ** 2));
                const angle = Math.round(Math.atan2(dy, dx) * (180 / Math.PI));
                const angle_corrected = Math.round(angle < 0 ? 360 + angle : angle);
                setDistance(distance);
                setAngleCorrected(angle_corrected);
            }
        };

        document.onmousemove = handleMouseMove;

        const currentcapRef = capRef.current;
        if (currentcapRef) {
            currentcapRef.onmousedown = () => setIsMouseDown(true);
        }

        return () => {
            document.onmouseup = null;
            document.onmousemove = null;
            if (currentcapRef) {
                currentcapRef.onmousedown = null;
            }
        };
    }, [isMouseDown, isSelected, centerX, centerY, cap_radius]);

    useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.key === 'Enter' && isSelected) {
                triggerMotion(index, distance, angle_corrected);
            }
        };

        document.addEventListener('keydown', handleKeyPress);

        return () => {
            document.removeEventListener('keydown', handleKeyPress);
        };
    }, [isSelected, triggerMotion, distance, angle_corrected, index]);

    return (
        <div ref={capRef} style={capStyle} onClick={handleCapClick}>
            {isSelected && <Arrow cap_radius={cap_radius} centerX={centerX} centerY={centerY} distance={distance} angle_corrected={angle_corrected} />}
            {showIndex && index !== 10 && <div style={indexStyle}>{index}</div>}
        </div>
    );
};

export default Cap;
