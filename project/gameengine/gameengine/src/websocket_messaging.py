"""
WebSocket messaging functionality for the gameengine app.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from project.gameengine.gameengine.src.channel_groups import get_user_group_name

def send_validation_message(user_id):
    """
    Send a validation message to a specific user via WebSocket.
    
    Args:
        user_id: The ID of the user to send the message to
        
    Returns:
        bool: True if the message was sent successfully
    """
    # Get the channel layer
    channel_layer = get_channel_layer()
    
    # Get the user's group name
    group_name = get_user_group_name(user_id)
    
    # Send a message to the group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'validation_message',
            'message': 'Validation successful! This message was sent via WebSocket.'
        }
    )
    
    return True
