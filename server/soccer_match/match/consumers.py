# match/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"match_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "match.message", "message": message}
        )
    
    # method that should be invoked on consumers that receive the event from the room group
    async def match_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        # The self.send method in the match_message function sends the message back to the 
        # WebSocket client that is connected to this instance of the consumer.
        await self.send(text_data=json.dumps({"message": message}))