import json
from channels.generic.websocket import AsyncWebsocketConsumer
from match.match_logic.main_match import Match
import numpy as np


match = Match()


class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Here: Established connection")
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'create_formation':
            await self.create_formation(data)
        elif action == 'submit_arrow':
            await self.submit_arrow(data)

    async def create_formation(self, data):
        print("Here: Creating formation")
        left_formation = data['left_formation']
        right_formation = data['right_formation']

        # Initial setup
        X_initial = match.initial_setup(left_formation, right_formation)

        response = {
            'initial_positions': X_initial.tolist(),
        }
        await self.send(text_data=json.dumps(response))

    async def submit_arrow(self, data):
        print("Here: Submitting arrow")
        cap_idx = int(data['cap_idx'])
        arrow_power = int(data['arrow_power'])
        angle = int(data['angle'])
        X_last = np.array(data['positions'])

        # Move cap
        X_hist = match.move_cap(cap_idx, arrow_power, angle, X_last)

        response = {
            'positions': [x.tolist() for x in X_hist]
        }
        await self.send(text_data=json.dumps(response))
