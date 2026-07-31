import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LeaderBoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'leaderboard_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def leaderboard_update_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'update',
            'data': message
        }))