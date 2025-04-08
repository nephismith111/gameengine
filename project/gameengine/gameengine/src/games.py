import json
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from gameengine.models import GameType, GameInstance
from gameengine.exceptions import GameEngineError

User = get_user_model()


class GameError(GameEngineError):
    """Base exception for game-related errors."""
    pass


def get_all_game_types():
    """
    Get all available game types.
    
    Returns:
        list: List of game types as dictionaries
    """
    game_types = GameType.objects.all()
    result = []
    
    for game_type in game_types:
        result.append({
            'id': game_type.id,
            'name': game_type.name,
            'description': game_type.description,
            'image_url': game_type.image_url,
            'max_players': game_type.max_players,
            'default_settings': game_type.default_settings
        })
    
    return result


def get_all_game_instances():
    """
    Get all game instances.
    
    Returns:
        list: List of game instances as dictionaries
    """
    game_instances = GameInstance.objects.all()
    result = []
    
    for instance in game_instances:
        result.append(format_game_instance(instance))
    
    return result


def get_game_instance(game_id):
    """
    Get a specific game instance by ID.
    
    Args:
        game_id (UUID): The ID of the game instance
        
    Returns:
        dict: Game instance as a dictionary
        
    Raises:
        GameError: If the game instance doesn't exist
    """
    try:
        instance = GameInstance.objects.get(id=game_id)
        return format_game_instance(instance)
    except GameInstance.DoesNotExist:
        raise GameError(f"Game instance with ID {game_id} not found")


def create_game_instance(game_type_id, instance_name, user):
    """
    Create a new game instance.
    
    Args:
        game_type_id (int): The ID of the game type
        instance_name (str): User-defined name for the game instance
        user (User): The user creating the game
        
    Returns:
        dict: The created game instance as a dictionary
        
    Raises:
        GameError: If the game type doesn't exist or other validation errors
    """
    try:
        game_type = GameType.objects.get(id=game_type_id)
    except GameType.DoesNotExist:
        raise GameError(f"Game type with ID {game_type_id} not found")
    
    # Initialize game data with joined users and game settings
    game_data = {
        'joined_users': [
            {
                'id': user.id,
                'username': user.username,
                'is_creator': True
            }
        ],
        'game_settings': game_type.default_settings.copy()
    }
    
    # Create the game instance
    instance = GameInstance.objects.create(
        game_type=game_type,
        instance_name=instance_name,
        status=GameInstance.Status.PENDING,
        game_data=game_data
    )
    
    return format_game_instance(instance)


def join_game_instance(game_id, user):
    """
    Join a game instance.
    
    Args:
        game_id (UUID): The ID of the game instance
        user (User): The user joining the game
        
    Returns:
        dict: The updated game instance as a dictionary
        
    Raises:
        GameError: If the game instance doesn't exist or can't be joined
    """
    try:
        instance = GameInstance.objects.get(id=game_id)
    except GameInstance.DoesNotExist:
        raise GameError(f"Game instance with ID {game_id} not found")
    
    # Check if the game is joinable
    if not instance.is_joinable:
        raise GameError("This game cannot be joined")
    
    # Check if the user is already in the game
    for joined_user in instance.joined_users:
        if joined_user.get('id') == user.id:
            return format_game_instance(instance)
    
    # Add the user to the joined_users list
    game_data = instance.game_data
    game_data['joined_users'].append({
        'id': user.id,
        'username': user.username,
        'is_creator': False
    })
    
    # Update the instance
    instance.game_data = game_data
    instance.save()
    
    return format_game_instance(instance)


def start_game_instance(game_id, user):
    """
    Start a game instance.
    
    Args:
        game_id (UUID): The ID of the game instance
        user (User): The user starting the game (must be the creator)
        
    Returns:
        dict: The updated game instance as a dictionary
        
    Raises:
        GameError: If the game instance doesn't exist or can't be started
    """
    try:
        instance = GameInstance.objects.get(id=game_id)
    except GameInstance.DoesNotExist:
        raise GameError(f"Game instance with ID {game_id} not found")
    
    # Check if the game is in pending status
    if instance.status != GameInstance.Status.PENDING:
        raise GameError("Only pending games can be started")
    
    # Check if the user is the creator
    creator_found = False
    for joined_user in instance.joined_users:
        if joined_user.get('id') == user.id and joined_user.get('is_creator', False):
            creator_found = True
            break
    
    if not creator_found:
        raise GameError("Only the game creator can start the game")
    
    # Update the instance status and started_datetime
    instance.status = GameInstance.Status.ONGOING
    instance.started_datetime = timezone.now()
    instance.save()
    
    return format_game_instance(instance)


def update_game_settings(game_id, user, game_settings):
    """
    Update the settings for a game instance.
    
    Args:
        game_id (UUID): The ID of the game instance
        user (User): The user updating the settings
        game_settings (dict): The new game settings
        
    Returns:
        GameInstance: The updated game instance
        
    Raises:
        GameError: If the game instance doesn't exist or the user is not the creator
    """
    try:
        instance = GameInstance.objects.get(id=game_id)
    except GameInstance.DoesNotExist:
        raise GameError(f"Game instance with ID {game_id} does not exist")
    
    # Check if the user is the creator
    creator_found = False
    for joined_user in instance.joined_users:
        if joined_user.get('id') == user.id and joined_user.get('is_creator', False):
            creator_found = True
            break
    
    if not creator_found:
        raise GameError("Only the game creator can update settings")
    
    # Check if the game is still pending
    if instance.status != GameInstance.Status.PENDING:
        raise GameError("Cannot update settings for a game that has already started or ended")
    
    # Update the settings
    game_data = instance.game_data
    game_data['game_settings'] = game_settings
    instance.game_data = game_data
    instance.save()
    
    # Send a WebSocket message to all users in the waiting room
    from project.gameengine.gameengine.src.websocket_messaging import send_settings_update_message
    send_settings_update_message(game_id, game_settings, user)
    
    return instance


def format_game_instance(instance):
    """
    Format a GameInstance model into a dictionary for API responses.
    
    Args:
        instance (GameInstance): The game instance to format
        
    Returns:
        dict: Formatted game instance
    """
    game_type = {
        'id': instance.game_type.id,
        'name': instance.game_type.name,
        'description': instance.game_type.description,
        'image_url': instance.game_type.image_url,
        'max_players': instance.game_type.max_players
    }
    
    return {
        'id': str(instance.id),
        'game_type': game_type,
        'instance_name': instance.instance_name,
        'status': instance.status,
        'created_datetime': instance.created_datetime.isoformat() if instance.created_datetime else None,
        'started_datetime': instance.started_datetime.isoformat() if instance.started_datetime else None,
        'ended_datetime': instance.ended_datetime.isoformat() if instance.ended_datetime else None,
        'player_count': instance.player_count,
        'joined_users': instance.joined_users,
        'is_joinable': instance.is_joinable,
        'game_settings': instance.game_data.get('game_settings', {})
    }
