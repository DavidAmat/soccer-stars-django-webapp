import React, { useState, useRef } from 'react';
import Cap from './Cap';
import './global.css'; // Import the global styles

const WEBSOCKET_URL = "ws://localhost:8000/ws/match/";

const App = () => {
    const [capConfigs, setCapConfigs] = useState([]);
    const [selectedCap, setSelectedCap] = useState(null);
    const positionsRef = useRef([]);
    const [time, setTime] = useState(0); // State for the clock
    const [intervalId, setIntervalId] = useState(null);
    const [isMotionInProgress, setIsMotionInProgress] = useState(false);
    // Create the score as a state  
    const [score, setScore] = useState([0, 0]);

    // Goal message
    const [isGoal, setIsGoal] = useState(false); // Add this state variable


    const LEFT_MARGIN = 207;
    const HORIZONTAL_MARGIN = 412;
    const TOP_MARGIN = 153;
    const DOWNSCALE_FACTOR_X = (1920 - HORIZONTAL_MARGIN) / 1920;
    const DOWNSCALE_FACTOR_Y = (1080 - TOP_MARGIN) / 1080;

    const scalePosition = (pos) => {
        return {
            x: pos[0] * DOWNSCALE_FACTOR_X + LEFT_MARGIN,
            y: pos[1] * DOWNSCALE_FACTOR_Y + TOP_MARGIN
        };
    };

    const handleStartMatch = () => {
        const ws = new WebSocket(WEBSOCKET_URL);

        ws.onopen = () => {
            const formationPayload = {
                action: "create_formation",
                left_formation: "formation1",
                right_formation: "formation2",
                // debug_formation: "debug_v1"
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
                    radius: index === response.initial_positions.length - 1 ? 27 : 52
                }));
                setCapConfigs(configs);
                positionsRef.current = response.initial_positions;
            }
            // Update score
            if (response.score) {
                setScore(response.score);
            }
            ws.close();
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        // Reset the clock
        setTime(0);
        if (intervalId) {
            clearInterval(intervalId);
        }
        const newIntervalId = setInterval(() => {
            setTime(prevTime => prevTime + 1);
        }, 1000);
        setIntervalId(newIntervalId);
    };

    const handleCapClick = (index) => {
        // Not allow selecting the ball, or select any cap if the motion is in progress
        if (!isMotionInProgress && index !== positionsRef.current.length - 1) {
            setSelectedCap(selectedCap === index ? null : index);
        }
    };

    const triggerMotion = (index, distance, angle_corrected) => {
        // Not allow moving the ball
        if (index === positionsRef.current.length - 1) {
            console.warn("Cannot move the ball directly");
            return;
        }


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
            setIsMotionInProgress(true); // Add this line before sending the WebSocket message
        };

        ws.onmessage = (event) => {
            const response = JSON.parse(event.data);

            // Log response
            console.log("Move Cap Response from WebSocket:", response);

            if (response.positions && response.score) {
                setSelectedCap(null); // De-select the cap
                const positions = response.positions;
                updatePositionsOverTime(positions, response.score, response.has_goal_timestep);
            }
            ws.close();
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    };

    const updatePositionsOverTime = (positions, score, hasGoalTimestep) => {
        let timestep = 0;

        const interval = setInterval(() => {
            if (timestep < positions.length) {
                const configs = positions[timestep].map((pos, index) => ({
                    pos: scalePosition(pos),
                    radius: index === positions[timestep].length - 1 ? 27 : 52
                }));
                setCapConfigs(configs);

                // GOAL MESSAGE
                if (hasGoalTimestep === timestep) {
                    setIsGoal(true);
                }

                timestep += 1;
            } else {
                clearInterval(interval);
                setIsMotionInProgress(false); // Allow user to interact again

                // Update the score
                if (score) {
                    setScore(score);
                }

                // Sleep for 1 second showing the GOAL MESSAGE
                setTimeout(() => {
                    setIsGoal(false);
                }, 1000); // 10000 ms (1000 timesteps with 10ms each)

                // Remember the last positions
                positionsRef.current = positions[positions.length - 1];

            }
        }, 10); // 10ms delay between each timestep
    };
    
    // Clock
    const formatTime = (time) => {
        const minutes = String(Math.floor(time / 60)).padStart(2, '0');
        const seconds = String(time % 60).padStart(2, '0');
        return `${minutes}:${seconds}`;
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
                {capConfigs.map((config, index) => (
                    <Cap
                        key={index}
                        index={index}
                        initialPosition={config.pos}
                        cap_radius={config.radius}
                        isSelected={selectedCap === index}
                        onCapClick={() => handleCapClick(index)}
                        triggerMotion={triggerMotion}
                        // set showIndex to true for debugging
                        showIndex={false}
                    />
                ))}
            </div>
            <div className="score-container">
                    <div className="score" id="score-team1">{score[0]}</div>
                    <div className="clock">{formatTime(time)}</div>
                    <div className="score" id="score-team2">{score[1]}</div>
            </div>
            {isGoal && (
                <div className="goal-message">GOAL !</div>
            )}
        </div>
    );
};

export default App;
