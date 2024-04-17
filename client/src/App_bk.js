import React, { useState } from 'react';

const App = () => {
    const [position] = useState({ x: 250, y: 250 }); // Circle's center
    // circle radius
    const [circle_radius] = useState(25);
    const [isSelected, setIsSelected] = useState(false);
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [arrowStyle, setArrowStyle] = useState({ display: 'none' }); // Initially hide the arrow
    const [maxLengthArrow, setMaxLengthArrow] = useState(100);

    const handleCircleClick = (e) => {
        const dx = e.clientX - (position.x);
        const dy = (position.y) - e.clientY;
        console.log("dx: ", dx, "dy: ", dy)
        const distanceFromCenter = Math.min(Math.sqrt(dx ** 2 + dy ** 2), maxLengthArrow);
        if (distanceFromCenter <= circle_radius) { // Assuming the circle's radius is 25
            setIsSelected(!isSelected);
            if (!isSelected) {
                // Reset arrow style to default when circle is selected
                setDefaultArrow();
            } else {
                // Hide arrow when circle is deselected
                setArrowStyle({ display: 'none' });
            }
        }
    };

    const handleMouseMove = (e) => {
        if (isMouseDown && isSelected) {
            const dx = e.clientX - position.x;
            const dy = position.y - e.clientY;
            const distance = Math.min(
                Math.max(
                    Math.sqrt(dx ** 2 + dy ** 2),
                    circle_radius
                ),
                maxLengthArrow
            );
            const angle = Math.atan2(dy, dx) * (180 / Math.PI);
            const angle_corrected = angle < 0 ? 360 + angle : angle;
            console.log("Angle: ", angle, "Angle_corrected: ", angle_corrected)
            setArrow(position.x, position.y, distance, angle_corrected);
        }
    };

    const setDefaultArrow = () => {
        setArrow(position.x, position.y, 100, 0); // Default distance and angle
    };

    const setArrow = (centerX, centerY, distance, angle_corrected) => {
        // Calculate the y-axis adjustment based on half of the arrow's height to center it vertically

        setArrowStyle({
            position: 'absolute',
            transformOrigin: '0% 50%',
            transform: `translate(${centerX}px, ${centerY - distance / 2}px) rotate(${-angle_corrected}deg)`,
            width: `${distance}px`,
            height: `${distance}px`,
            pointerEvents: 'none',
            display: 'block',
            backgroundImage: 'url("/icons/arrow.svg")',
            backgroundSize: 'contain',
            backgroundRepeat: 'no-repeat',
        });
    };

    // Listen to document-level events for mouse down and up
    document.onmousedown = () => setIsMouseDown(true);
    document.onmouseup = () => setIsMouseDown(false);
    document.onclick = handleCircleClick;
    document.onmousemove = handleMouseMove;

    return (
        <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
            <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                backgroundColor: isSelected ? 'red' : 'black',
                position: 'absolute',
                left: `${position.x - 25}px`,
                top: `${position.y - 25}px`,
            }} />
            <div style={arrowStyle} />
        </div>
    );
};

export default App;
