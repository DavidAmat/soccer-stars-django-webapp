// src/hooks/useMotionCircle.js
import { useState, useEffect } from 'react';

const useMotionCircle = (configs, motionData, timestep) => {
    const [positions, setPositions] = useState(configs.map(config => config.initialPosition));
    const [counter, setCounter] = useState(1);

    useEffect(() => {
        const interval = setInterval(() => {
            if (counter <= Object.keys(motionData).length) {
                const moves = motionData[counter];
                setPositions(currentPositions =>
                    currentPositions.map((position, index) => {
                        const move = moves.find(move => move.index === index);
                        return move ? move.newPosition : position;
                    })
                );
                setCounter(counter => counter + 1);
            }
        }, timestep * 500);

        return () => clearInterval(interval);
    }, [motionData, timestep]);

    return positions;
};

export default useMotionCircle;