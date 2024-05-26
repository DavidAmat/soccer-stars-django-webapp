// src/App.js
import React, { useState, useEffect, useCallback } from 'react';
import Circle from './Circle';
import useMotionCircle from './hooks/useMotionCircle';
import './global.css'; // Import the global styles

const WEBSOCKET_URL = "ws://localhost:8000/ws/match/";

const App = () => {
    const [selectedCircle, setSelectedCircle] = useState(null);
    const [configs, setConfigs] = useState([
        { initialPosition: { x: 250, y: 550 }, circle_radius: 50 },
        { initialPosition: { x: 350, y: 850 }, circle_radius: 50 },
        { initialPosition: { x: 550, y: 850 }, circle_radius: 50 },
        // Add more circle configs here
    ]);
    const [newConfigs, setNewConfigs] = useState(null); // Define newConfigs as a state variable

    const fetchInitialPositions = useCallback(() => {
        const ws = new WebSocket(WEBSOCKET_URL);

        ws.onopen = () => {
            const formationPayload = {
                action: "create_formation",
                left_formation: "formation1",
                right_formation: "formation2"
            };
            console.log("Sending to WebSocket:", formationPayload);
            ws.send(JSON.stringify(formationPayload));
        };

        ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            console.log("Received from WebSocket:", response);
            console.log("Initial configs:", configs);
            if (response.initial_positions) {
                const newConfigsData = response.initial_positions.map(position => ({
                    initialPosition: { x: position[0], y: position[1] },
                    circle_radius: 50
                }));
                setNewConfigs(newConfigsData); // Update newConfigs instead of configs
            }
            ws.close();
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }, []);

    useEffect(() => {
        fetchInitialPositions();
    }, [fetchInitialPositions]);

    const calculateNewPosition = (initialPosition, distance, angle) => {
        const angleInRadians = angle * (Math.PI / 180);
        const x = Math.round(initialPosition.x + distance * Math.cos(angleInRadians));
        const y = Math.round(initialPosition.y - distance * Math.sin(angleInRadians));
        return { x, y };
    };

    const calculateMotion = (circleIndex, distance, angle_corrected) => {
        const currentConfigs = newConfigs || configs; // Use newConfigs if available, else fall back to configs
        const motion = {};
        let currentDistance = distance;
        let timestep = 1;

        while (currentDistance >= 1) {
            const newPosition = calculateNewPosition(currentConfigs[circleIndex].initialPosition, currentDistance, angle_corrected);
            if (!motion[timestep]) {
                motion[timestep] = [];
            }
            motion[timestep].push({ index: circleIndex, newPosition });
            console.log('calculateMotion: [timestep]:', timestep, '[circleIndex]:', circleIndex, '[newPosition]:', newPosition);

            currentDistance /= 2;
            timestep += 1;
        }

        return motion;
    };

    const handleMotionTrigger = (index, distance, angle_corrected) => {
        const ws = new WebSocket(WEBSOCKET_URL);

        ws.onopen = () => {
            const arrowPayload = {
                action: "submit_arrow",
                cap_idx: index,
                arrow_power: distance,
                angle: angle_corrected,
                positions: (newConfigs || configs).map(config => [config.initialPosition.x, config.initialPosition.y])
            };
            ws.send(JSON.stringify(arrowPayload));
        };

        ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            if (response.positions) {
                const newPositions = response.positions.map(position => ({
                    initialPosition: { x: position[0], y: position[1] },
                    circle_radius: 50
                }));
                setNewConfigs(newPositions); // Update newConfigs with the new positions
            }
            ws.close();
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    };

    const positions = useMotionCircle(newConfigs || configs, calculateMotion, 0.5); // Use newConfigs if available, else fall back to configs

    const handleCircleClick = (index) => {
        setSelectedCircle(selectedCircle === index? null : index);
    };

    return (
        <div id="root">
            <div className="background"></div>
            <div className="game-container">
                {positions.map((position, index) => (
                    <Circle
                        key={index}
                        index={index}
                        initialPosition={position}
                        circle_radius={(newConfigs || configs)[index].circle_radius}
                        isSelected={selectedCircle === index}
                        onCircleClick={() => handleCircleClick(index)}
                        triggerMotion={handleMotionTrigger}
                    />
                ))}
            </div>
        </div>
    );
};

export default App;
