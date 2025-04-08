"""
WebSocket messaging functionality for the gameengine app.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from project.gameengine.gameengine.src.channel_groups import get_user_group_name, get_waiting_room_group_name

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
            'message': 'Validation successful! This message was sent via WebSocket.',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
    )
    
    return True


def send_settings_update_message(game_id, game_settings, user):
    """
    Send a settings update message to all users in a waiting room.
    
    Args:
        game_id (UUID): The ID of the game instance
        game_settings (dict): The updated game settings
        user (User): The user who updated the settings
        
    Returns:
        bool: True if the message was sent successfully
    """
    # Get the channel layer
    channel_layer = get_channel_layer()
    
    # Get the waiting room group name
    group_name = get_waiting_room_group_name(game_id)
    
    # Send the message to the waiting room group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'settings_update',
            'message_type': 'settings_update',
            'game_settings': game_settings,
            'updated_by': {
                'id': user.id,
                'username': user.username
            },
            'timestamp': datetime.now().isoformat()
        }
    )
    
    return True
