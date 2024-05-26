// src/Circle.js
import React, { useState, useEffect, useRef } from 'react';
import Arrow from './Arrow';

const Circle = ({ initialPosition, circle_radius, isSelected, onCircleClick, index, triggerMotion }) => {
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [distance, setDistance] = useState(100); // Default distance
    const [angle_corrected, setAngleCorrected] = useState(0); // Default angle
    const circleRef = useRef(null); // Reference to the circle div

    const circleStyle = {
        width: `${circle_radius * 2}px`,
        height: `${circle_radius * 2}px`,
        position: 'absolute',
        left: `${initialPosition.x - circle_radius}px`,
        top: `${initialPosition.y - circle_radius}px`,
        backgroundImage: 'url("/icons/cap_f1.svg")',
        backgroundSize: 'contain',
        backgroundRepeat: 'no-repeat',
        cursor: 'pointer'
    };

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

        const currentCircleRef = circleRef.current;
        if (currentCircleRef) {
            currentCircleRef.onmousedown = () => setIsMouseDown(true);
        }

        return () => {
            document.onmouseup = null;
            document.onmousemove = null;
            if (currentCircleRef) {
                currentCircleRef.onmousedown = null;
            }
        };
    }, [isMouseDown, isSelected, centerX, centerY, circle_radius]);

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
        <div ref={circleRef} style={circleStyle} onClick={handleCircleClick}>
            {isSelected && <Arrow circle_radius={circle_radius} centerX={centerX} centerY={centerY} distance={distance} angle_corrected={angle_corrected} />}
        </div>
    );
};

export default Circle;
