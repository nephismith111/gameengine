"""
Interface for the worker app.
Exposes functions for other apps to interact with the simulation worker.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def start_game_simulation(game_id, settings=None):
    """
    Start a simulation for a game.
    
    Args:
        game_id: UUID of the game instance
        settings: Optional dictionary of game settings
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        "simulation",
        {
            "type": "start_simulation",
            "game_id": str(game_id),
            "settings": settings or {}
        }
    )


def stop_game_simulation(game_id):
    """
    Stop a simulation for a game.
    
    Args:
        game_id: UUID of the game instance
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        "simulation",
        {
            "type": "stop_simulation",
            "game_id": str(game_id)
        }
    )


def update_game_entity(game_id, entity_id, entity_data):
    """
    Update an entity in a game simulation.
    
    Args:
        game_id: UUID of the game instance
        entity_id: ID of the entity to update
        entity_data: Dictionary of entity data
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        "simulation",
        {
            "type": "update_entity",
            "game_id": str(game_id),
            "entity_id": entity_id,
            "entity_data": entity_data
        }
    )


def update_game_settings(game_id, settings):
    """
    Update settings for a game simulation.
    
    Args:
        game_id: UUID of the game instance
        settings: Dictionary of game settings
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        "simulation",
        {
            "type": "update_settings",
            "game_id": str(game_id),
            "settings": settings
        }
    )
