// src/Circle.js
import React, { useState, useEffect, useRef } from 'react';
import Arrow from './Arrow';

const Circle = ({ initialPosition, circle_radius, isSelected, onCircleClick, index }) => {
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [distance, setDistance] = useState(100); // Default distance
    const [angle_corrected, setAngleCorrected] = useState(0); // Default angle
    const circleRef = useRef(null); // Reference to the circle div

    const handleCircleClick = (e) => {
        const dx = e.clientX - initialPosition.x;
        const dy = initialPosition.y - e.clientY;
        const distanceFromCenter = Math.sqrt(dx ** 2 + dy ** 2);
        if (distanceFromCenter <= circle_radius) {
            onCircleClick();
        }
    };

    // Logs
    useEffect(() => {
        console.log(`Circle ${index} isSelected state changed: ${isSelected ? 'Selected' : 'Not selected'}, isMouseDown: ${isMouseDown}`);
    }, [isSelected, isMouseDown]);

    // Reset isMouseDown state when isSelected state changes
    useEffect(() => {
        if (isSelected) {
            setIsMouseDown(false);
        }
    }, [isSelected]);

    const handleMouseMove = (e) => {
        if (isMouseDown && isSelected) {
            const dx = e.clientX - initialPosition.x;
            const dy = initialPosition.y - e.clientY;
            const distance = Math.min(
                Math.max(
                    Math.sqrt(dx ** 2 + dy ** 2),
                    circle_radius
                ),
                100 // Maximum length of the arrow
            );
            const angle = Math.atan2(dy, dx) * (180 / Math.PI);
            const angle_corrected = angle < 0 ? 360 + angle : angle;
            setDistance(distance);
            setAngleCorrected(angle_corrected);
            console.log(`Distance: ${distance}, Angle: ${angle_corrected}`);
        }
    };

    useEffect(() => {
        // Listen to document-level events for mouse up and move
        document.onmouseup = () => setIsMouseDown(false);
        document.onmousemove = handleMouseMove;

        // Listen to circle-level event for mouse down
        if (circleRef.current) {
            circleRef.current.onmousedown = () => setIsMouseDown(true);
        }

        // Clean up the event listeners when the component unmounts
        return () => {
            document.onmouseup = null;
            document.onmousemove = null;
            if (circleRef.current) {
                circleRef.current.onmousedown = null;
            }
        };
    }, [isMouseDown, isSelected]);

    return (
        <div ref={circleRef} onClick={handleCircleClick} style={{ position: 'absolute', left: `${initialPosition.x}px`, top: `${initialPosition.y}px` }}>
            <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                backgroundColor: isSelected ? 'red' : 'black',
                position: 'absolute',
                left: `-${circle_radius}px`,
                top: `-${circle_radius}px`,
            }} />
            {isSelected && <Arrow centerX={initialPosition.x} centerY={initialPosition.y} distance={distance} angle_corrected={angle_corrected} />}
        </div>
    );
};

export default Circle;