import React, { useState, useEffect, useRef } from 'react';
import Circle from './Circle';
import './global.css'; // Import the global styles

const WEBSOCKET_URL = "ws://localhost:8000/ws/match/";

const App = () => {
    const [circleConfigs, setCircleConfigs] = useState([]);
    const [selectedCircle, setSelectedCircle] = useState(null);
    const positionsRef = useRef([]);

    const LEFT_MARGIN = 207;
    const TOP_MARGIN = 183;
    const DOWNSCALE_FACTOR = 0.793;

    const scalePosition = (pos) => {
        return {
            x: pos[0] * DOWNSCALE_FACTOR + LEFT_MARGIN,
            y: pos[1] * DOWNSCALE_FACTOR + TOP_MARGIN
        };
    };

    const handleStartMatch = () => {
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
            if (response.initial_positions) {
                const configs = response.initial_positions.map((pos, index) => ({
                    pos: scalePosition(pos),
                    radius: index === response.initial_positions.length - 1 ? 25 : 50
                }));
                setCircleConfigs(configs);
                positionsRef.current = response.initial_positions;
            }
            ws.close();
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    };

    const handleCircleClick = (index) => {
        setSelectedCircle(selectedCircle === index ? null : index);
    };

    const triggerMotion = (index, distance, angle_corrected) => {
        const ws = new WebSocket(WEBSOCKET_URL);

        ws.onopen = () => {
            const arrowPayload = {
                action: "submit_arrow",
                cap_idx: index,
                arrow_power: distance,
                angle: angle_corrected,
                positions: positionsRef.current
            };
            console.log("Sending to WebSocket:", arrowPayload);
            ws.send(JSON.stringify(arrowPayload));
        };

        ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            if (response.positions) {
                setSelectedCircle(null); // De-select the cap
                const positions = response.positions;
                updatePositionsOverTime(positions);
            }
            ws.close();
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    };

    const updatePositionsOverTime = (positions) => {
        let timestep = 0;

        const interval = setInterval(() => {
            if (timestep < positions.length) {
                const configs = positions[timestep].map((pos, index) => ({
                    pos: scalePosition(pos),
                    radius: index === positions[timestep].length - 1 ? 25 : 50
                }));
                setCircleConfigs(configs);
                timestep += 1;
            } else {
                clearInterval(interval);
                // Remember the last positions
                positionsRef.current = positions[positions.length - 1];
            }
        }, 10); // 10ms delay between each timestep
    };

    return (
        <div id="root">
            <div className="background"></div>
            <div className="button-container">
                <button className="start-button" onClick={handleStartMatch}>
                    Start Match
                </button>
            </div>
            <div className="game-container">
                {circleConfigs.map((config, index) => (
                    <Circle
                        key={index}
                        index={index}
                        initialPosition={config.pos}
                        circle_radius={config.radius}
                        isSelected={selectedCircle === index}
                        onCircleClick={() => handleCircleClick(index)}
                        triggerMotion={triggerMotion}
                    />
                ))}
            </div>
        </div>
    );
};

export default App;
