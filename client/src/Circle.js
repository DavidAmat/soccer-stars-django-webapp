// src/Circle.js
import React, { useState, useEffect, useRef } from 'react';
import Arrow from './Arrow';

const Circle = ({ initialPosition, circle_radius, isSelected, onCircleClick, index }) => {
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [distance, setDistance] = useState(100); // Default distance
    const [angle_corrected, setAngleCorrected] = useState(0); // Default angle
    const circleRef = useRef(null); // Reference to the circle div

    // Adjust the initialPosition to be the top-left corner of the circle
    const circleStyle = {
        width: `${circle_radius * 2}px`,
        height: `${circle_radius * 2}px`,
        borderRadius: '50%',
        backgroundColor: isSelected ? 'red' : 'black',
        position: 'absolute',
        left: `${initialPosition.x - circle_radius}px`,
        top: `${initialPosition.y - circle_radius}px`,
    };

    // Adjust the centerX and centerY to be the center of the circle
    const centerX = initialPosition.x;
    const centerY = initialPosition.y;

    const handleCircleClick = (e) => {
        const dx = e.clientX - centerX;
        const dy = centerY - e.clientY;
        const distanceFromCenter = Math.sqrt(dx ** 2 + dy ** 2);
        if (distanceFromCenter <= circle_radius) {
            onCircleClick();
        }
    };

    // Logs
    useEffect(() => {
        console.log(`Circle ${index} isSelected state changed: ${isSelected ? 'Selected' : 'Not selected'}, isMouseDown: ${isMouseDown}`);
    }, [isSelected, isMouseDown, index]);

    // Reset isMouseDown state when isSelected state changes
    useEffect(() => {
        if (isSelected) {
            setIsMouseDown(false);
        }
    }, [isSelected]);

    

    useEffect(() => {
        // Listen to document-level events for mouse up and move
        document.onmouseup = () => setIsMouseDown(false);

        const handleMouseMove = (e) => {
            if (isMouseDown && isSelected) {
                const dx = e.clientX - centerX;
                const dy = centerY - e.clientY;
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
            }
        };


        document.onmousemove = handleMouseMove;

        // Listen to circle-level event for mouse down
        const currentCircleRef = circleRef.current; // Copy 'circleRef.current' to a variable
        if (currentCircleRef) {
            currentCircleRef.onmousedown = () => setIsMouseDown(true);
        }

        // Clean up the event listeners when the component unmounts
        return () => {
            document.onmouseup = null;
            document.onmousemove = null;
            if (currentCircleRef) {
                currentCircleRef.onmousedown = null;
            }
        };
    }, [isMouseDown, isSelected, centerX, centerY, circle_radius]);

    return (
        <div ref={circleRef} style={circleStyle} onClick={handleCircleClick}>
            {isSelected && <Arrow circle_radius={circle_radius} centerX={centerX} centerY={centerY} distance={distance} angle_corrected={angle_corrected} />}
        </div>
    );
};

export default Circle;