from gameengine.exceptions import GameEngineError

class UserAuthError(GameEngineError):
    """Base exception for user authentication errors"""
    pass

class RegistrationError(UserAuthError):
    """Exception raised when user registration fails"""
    pass
