"""
WebSocket consumer for the gameengine app.
"""
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
import uuid
from project.gameengine.gameengine.src.channel_groups import get_user_group_name

class ValidateConsumer(WebsocketConsumer):
    """
    Consumer to validate WebSocket connections and handle messages.
    """
    
    def connect(self):
        """
        Called when the WebSocket is handshaking as part of initial connection.
        """
        # Accept the connection
        self.accept()
        
        # Get the user from the scope
        user = self.scope.get("user", None)
        
        # Add the user to appropriate groups
        if user and user.is_authenticated:
            # Add to user-specific group
            self.user_group = get_user_group_name(user.id)
            async_to_sync(self.channel_layer.group_add)(
                self.user_group,
                self.channel_name
            )
        else:
            # Use a unique identifier for anonymous users
            self.user_group = f"anonymous_{uuid.uuid4().hex}"
            async_to_sync(self.channel_layer.group_add)(
                self.user_group,
                self.channel_name
            )
        
        # Send a connection confirmation message
        self.send(text_data=json.dumps({
            'message_type': 'connection_established',
            'message': 'WebSocket connection established'
        }))
    
    def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the user group
        if hasattr(self, 'user_group'):
            async_to_sync(self.channel_layer.group_discard)(
                self.user_group,
                self.channel_name
            )
    
    def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        # Parse the received JSON
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            # Echo the message back to the client
            self.send(text_data=json.dumps({
                'type': 'echo_message',
                'message': f"Echo: {message}"
            }))
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    def validation_message(self, event):
        """
        Handler for validation_message event.
        """
        # Send the validation message to the WebSocket
        self.send(text_data=json.dumps({
            'message_type': 'validation',
            'message': event['message'],
            'user_id': event.get('user_id'),
            'timestamp': event.get('timestamp')
        }))


class WaitingRoomConsumer(WebsocketConsumer):
    """
    Consumer for waiting room WebSocket connections.
    Handles real-time updates for waiting room state.
    """
    
    def connect(self):
        """
        Called when the WebSocket is handshaking as part of initial connection.
        """
        # Accept the connection
        self.accept()
        
        # Get the user from the scope
        user = self.scope.get("user", None)
        
        # Get the URL path components to extract game_id
        path = self.scope['path']
        import re
        match = re.search(r'waitingroom/([0-9a-f-]+)', path)
        
        if not match:
            # Invalid URL format
            self.close(code=4000)
            return
            
        # Extract game_id from the path
        self.game_id = match.group(1)
        
        # Add the user to appropriate groups
        if user and user.is_authenticated:
            # Add to user-specific group
            self.user_group = get_user_group_name(user.id)
            async_to_sync(self.channel_layer.group_add)(
                self.user_group,
                self.channel_name
            )
            
            # Add to waiting room group
            from project.gameengine.gameengine.src.channel_groups import get_waiting_room_group_name
            self.waiting_room_group = get_waiting_room_group_name(self.game_id)
            async_to_sync(self.channel_layer.group_add)(
                self.waiting_room_group,
                self.channel_name
            )
            
            # Send a connection confirmation message
            self.send(text_data=json.dumps({
                'message_type': 'connection_established',
                'message': 'Waiting room WebSocket connection established',
                'game_id': self.game_id
            }))
        else:
            # Close connection for unauthenticated users
            self.close(code=4001)
    
    def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the user group
        if hasattr(self, 'user_group'):
            async_to_sync(self.channel_layer.group_discard)(
                self.user_group,
                self.channel_name
            )
        
        # Leave the waiting room group
        if hasattr(self, 'waiting_room_group'):
            async_to_sync(self.channel_layer.group_discard)(
                self.waiting_room_group,
                self.channel_name
            )
    
    def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        # Parse the received JSON
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('message_type', '')
            
            # Handle different message types
            if message_type == 'ping':
                self.send(text_data=json.dumps({
                    'message_type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
            else:
                self.send(text_data=json.dumps({
                    'message_type': 'error',
                    'message': f"Unknown message type: {message_type}"
                }))
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'message_type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    def settings_update(self, event):
        """
        Handler for settings_update event.
        """
        # Send the settings update message to the WebSocket
        self.send(text_data=json.dumps({
            'message_type': event['message_type'],
            'game_settings': event['game_settings'],
            'updated_by': event['updated_by'],
            'timestamp': event['timestamp']
        }))
        
        # Log that we sent the message
        print(f"WebSocket message sent: settings_update to {self.game_id}")
    
    def waitingroom_update(self, event):
        """
        Handler for waitingroom_update event.
        Sends comprehensive waiting room state updates.
        """
        # Forward the waiting room update to the client
        self.send(text_data=json.dumps({
            'message_type': 'waitingroom_update',
            'game_data': event['game_data'],
            'timestamp': event['timestamp']
        }))
        
        # Log that we sent the message
        print(f"WebSocket message sent: waitingroom_update to {self.game_id}")
