"""
Channel group naming utilities for WebSocket communication.

This module centralizes all channel group name generation to ensure consistency
across the application. Never hardcode channel group names in WebSocket consumers
or messaging functions - always use these functions.
"""

def get_user_group_name(user_id):
    """
    Get the channel group name for a specific user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: The channel group name for the user
    """
    return f"user_{user_id}"

def get_game_group_name(game_id):
    """
    Get the channel group name for a specific game.
    
    Args:
        game_id: The ID of the game instance
        
    Returns:
        str: The channel group name for the game
    """
    return f"game_{game_id}"

def get_waiting_room_group_name(game_id):
    """
    Get the channel group name for a specific waiting room.
    
    Args:
        game_id: The ID of the game instance
        
    Returns:
        str: The channel group name for the waiting room
    """
    return f"waiting_room_{game_id}"
