import json
from channels.generic.websocket import AsyncWebsocketConsumer
from match.match_logic.main_match import Match
import numpy as np

import logging

# Get a logger instance
logger = logging.getLogger(__name__)


match = Match()


class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("CONNECT: Established connection")
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "create_formation":
            await self.create_formation(data)
        elif action == "submit_arrow":
            await self.submit_arrow(data)

    async def create_formation(self, data):
        logger.info("CREATE_FORMATION: Creating formation")
        left_formation = data["left_formation"]
        right_formation = data["right_formation"]
        debug_formation = data.get("debug_formation")

        # If provided, get the scale factor and margins for transforming 2D coordinates
        scale_factor = tuple(data.get("scale_factor", (1, 1)))
        margin = tuple(data.get("margin", (0, 0)))

        # Initial setup
        X_initial = match.initial_setup(left_formation, right_formation, debug_formation=debug_formation)
        X_initial = X_initial.tolist()

        # Scale and adjust coordinates
        X_scaled = match.adjust_coordinates(positions=X_initial, scale_factor=scale_factor, margin=margin)

        response = {"initial_positions": X_initial, "scaled_positions": X_scaled, "score": match.score}
        await self.send(text_data=json.dumps(response))

    async def submit_arrow(self, data):
        logger.info("SUBMIT_ARROW: Submitting arrow")
        cap_idx = int(data["cap_idx"])
        arrow_power = int(data["arrow_power"])
        angle = int(data["angle"])
        X_last = np.array(data["positions"])

        # Move cap
        X_hist, metadata = match.move_cap(cap_idx, arrow_power, angle, X_last)

        response = {
            "positions": [x.tolist() for x in X_hist],
            "score": match.score,
            "has_goal": metadata.get("has_goal", False),
            "has_goal_timestep": metadata.get("has_goal_timestep", None),
        }
        await self.send(text_data=json.dumps(response))
