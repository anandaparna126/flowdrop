import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class FlowChartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("coming inside def connect in consumers")
        self.chart_id = self.scope['url_route']['kwargs']['chart_id']
        self.room_group = f'chart_{self.chart_id}'
        self.user_info = None
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("coming inside def disconnect in consumers")
        if self.user_info:
            await self.channel_layer.group_send(self.room_group, {
                'type': 'user_left',
                'user_id': self.user_info['user_id'],
                'username': self.user_info['username']
            })
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        print("coming inside def receive in consumers")
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'join':
            print("coming inside msg type is join in consumers")
            self.user_info = {
                'user_id': data['user_id'],
                'username': data['username'],
                'avatar_color': data.get('avatar_color', '#6366f1')
            }
            await self.channel_layer.group_send(self.room_group, {
                'type': 'user_joined',
                **self.user_info,
                'channel': self.channel_name
            })

        elif msg_type == 'cursor_move':
            print("coming inside msg type is cursor move in consumers")
            await self.channel_layer.group_send(self.room_group, {
                'type': 'cursor_update',
                'user_id': data['user_id'],
                'username': data['username'],
                'avatar_color': data.get('avatar_color', '#6366f1'),
                'x': data['x'],
                'y': data['y'],
                'channel': self.channel_name
            })

        elif msg_type == 'canvas_change':
            print("coming inside msg type is canvas change in consumers")
            await self.channel_layer.group_send(self.room_group, {
                'type': 'canvas_updated',
                'user_id': data['user_id'],
                'username': data['username'],
                'canvas_data': data['canvas_data'],
                'change_type': data.get('change_type', 'update'),
                'channel': self.channel_name
            })

        elif msg_type == 'node_select':
            print("coming inside msg type is node select in consumers")
            await self.channel_layer.group_send(self.room_group, {
                'type': 'node_selected',
                'user_id': data['user_id'],
                'username': data['username'],
                'avatar_color': data.get('avatar_color', '#6366f1'),
                'node_id': data.get('node_id'),
                'channel': self.channel_name
            })

    async def user_joined(self, event):
        print("coming inside user joined function in consumers")
        if event.get('channel') != self.channel_name:
            await self.send(text_data=json.dumps({'type': 'user_joined', 'user_id': event['user_id'], 'username': event['username'], 'avatar_color': event['avatar_color']}))

    async def user_left(self, event):
        print("coming inside user left function in consumers")
        await self.send(text_data=json.dumps({'type': 'user_left', 'user_id': event['user_id'], 'username': event['username']}))

    async def cursor_update(self, event):
        print("coming inside cursor update function in consumers")
        if event.get('channel') != self.channel_name:
            await self.send(text_data=json.dumps({'type': 'cursor_move', 'user_id': event['user_id'], 'username': event['username'], 'avatar_color': event['avatar_color'], 'x': event['x'], 'y': event['y']}))

    async def canvas_updated(self, event):
        print("coming inside canvas updated function in consumers")
        if event.get('channel') != self.channel_name:
            await self.send(text_data=json.dumps({'type': 'canvas_change', 'user_id': event['user_id'], 'username': event['username'], 'canvas_data': event['canvas_data'], 'change_type': event['change_type']}))

    async def node_selected(self, event):
        print("coming inside node selected fucntion in consumers")
        if event.get('channel') != self.channel_name:
            await self.send(text_data=json.dumps({'type': 'node_select', 'user_id': event['user_id'], 'username': event['username'], 'avatar_color': event['avatar_color'], 'node_id': event['node_id']}))
