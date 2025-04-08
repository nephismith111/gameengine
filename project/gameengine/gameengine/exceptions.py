"""
Defines custom exceptions specific to the app
"""

class GameEngineError(Exception):
    """Base exception for all game engine errors"""
    pass

class InvalidGameStateError(GameEngineError):
    """Raised when an operation is attempted in an invalid game state"""
    pass

class PlayerNotFoundError(GameEngineError):
    """Raised when a player is not found"""
    pass
