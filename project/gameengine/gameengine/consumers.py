"""
WebSocket consumer for the gameengine app.
"""
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

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
        
        # Add the user to a group based on their username or a random identifier
        if user and user.is_authenticated:
            self.group_name = f"user_{user.id}"
        else:
            # Use a unique identifier for anonymous users
            import uuid
            self.group_name = f"anonymous_{uuid.uuid4().hex}"
        
        # Join the group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        
        # Send a connection confirmation message
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket connection established'
        }))
    
    def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the group
        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
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
            'type': 'validation_message',
            'message': event['message']
        }))
