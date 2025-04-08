"""
Channel group naming utilities for WebSocket communication.
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
