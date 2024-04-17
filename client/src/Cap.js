import React, { useRef, useEffect, useState } from 'react';
import CapArrow from './CapArrow';

const Cap = ({ capIndex, capCenter, capRadius, isSelected, onCapClick, onCapSubmit }) => {

    // Reference to the Cap div
    const CapRef = useRef(null); 

    // Create a state to indicate if the mouse is down
    const [isMouseDown, setIsMouseDown] = useState(false);

    // Create a state to store the distance and angle of the arrow
    const [distance, setDistance] = useState(100); // Default distance
    const [angle, setAngle] = useState(0); // Default angle

    // --------------------------------------------------------------- 
    //   Initial positions
    // --------------------------------------------------------------- 
    // Adjust the initialPosition to be the top-left corner of the Cap
    const capStyle = {
        width: `${capRadius * 2}px`,
        height: `${capRadius * 2}px`,
        borderRadius: '50%',
        backgroundColor: isSelected ? 'red' : 'black',
        position: 'absolute',
        left: `${capCenter.x - capRadius}px`,
        top: `${capCenter.y - capRadius}px`,
    };

    // Handle Click on the Cap
    const handleCapClick = (e) => {
        const dx = e.clientX - capCenter.x;
        const dy = -(e.clientY - capCenter.y);
        const distanceFromCenterCap = Math.round(Math.sqrt(dx ** 2 + dy ** 2));
        if (distanceFromCenterCap <= capRadius) {
            onCapClick();
        }
        console.log("Cap clicked: ", capIndex);
        console.log("Distance from center: ", distanceFromCenterCap)
    };

    // --------------------------------------------------------------- 
    // Arrow creation when a Cap is selected and pressing the mouse on 
    // --------------------------------------------------------------- 
    // Reset isMouseDown state when isSelected state changes
    // if a cap is just selected, then the mouse is not down 
    useEffect(() => {
        if (isSelected) {
            setIsMouseDown(true);
        }
    }, [isSelected]);

    // Create the effect to create the arrow distance and angle
    useEffect(() => {

        // Listen to document-level events for mouse up and move
        document.onmouseup = () => setIsMouseDown(false);

        const handleMouseMove = (e) => {
            if (isSelected && isMouseDown) {
                // Distance to the Cap center
                const dx = e.clientX - capCenter.x;
                const dy = - (e.clientY - capCenter.y);
                const distance = Math.round(Math.min(
                    Math.max(
                        Math.sqrt(dx ** 2 + dy ** 2),
                        capRadius
                    ),
                    200
                ));
                setDistance(distance);

                // Calculate angle of the power arrow and correct the angle if it is negative
                const angle_raw = Math.atan2(dy, dx) * (180 / Math.PI);
                const angle = Math.round(angle_raw < 0 ? 360 + angle_raw : angle_raw);
                setAngle(angle);
            }
        };

        document.onmousemove = handleMouseMove;

        // When that Cap is clicked (onmousedown) it will activate the mouse down state
        // hence, the handleMouseMove will be called, so that the states distance and angle are updated
        const currentCapRef = CapRef.current; // Copy 'CapRef.current' to a variable
        if (currentCapRef) {
            currentCapRef.onmousedown = () => setIsMouseDown(true);
        }

        // Clean up the event listeners when the component unmounts
        return () => {
            document.onmouseup = null;
            document.onmousemove = null;
            if (currentCapRef) {
                currentCapRef.onmousedown = null;
            }
        };

    }, [isMouseDown, isSelected, distance, angle]);

    // ---------------------------------------------------------------
    // ---------------------------------------------------------------

    // --------------------------------------------------------------- 
    // Cap Submit Arrow power 
    // --------------------------------------------------------------- 

    useEffect(() => {
        // Define the handler that will be triggered at each keydown
        const handleKeyDown = (e) => {
            if (e.key === 'Enter') {
                // handleCapSubmit = (capIndex, distance, angle)
                onCapSubmit(capIndex, distance, angle);
            }
        };
    
        // Call the handler when a keydown is pressed at any place of the page (document)
        if (isSelected) {
            document.addEventListener('keydown', handleKeyDown);
        }
    
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isSelected, capIndex, distance, angle, onCapSubmit]);

    return (
        <div style={capStyle} onClick={handleCapClick}>
            {isSelected && <CapArrow capRadius={capRadius} distance={distance} angle={angle} />}
        </div>
    );

};

export default Cap;