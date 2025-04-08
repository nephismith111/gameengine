"""
Custom middleware for WebSocket authentication.
"""
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.http.cookie import SimpleCookie
import datetime

User = get_user_model()

@database_sync_to_async
def get_user(session_key):
    """
    Get the user from the session key.
    """
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        
        if user_id:
            return User.objects.get(id=user_id)
        return AnonymousUser()
    except (Session.DoesNotExist, User.DoesNotExist):
        return AnonymousUser()

class WebSocketAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that populates scope["user"] from the session.
    """
    
    async def __call__(self, scope, receive, send):
        """
        Process the scope and add the user to it.
        """
        # Parse cookies from headers using Django's SimpleCookie
        cookies = {}
        headers = dict(scope.get('headers', []))
        cookie_header = headers.get(b'cookie', b'').decode('utf-8')
        
        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            cookies = {k: v.value for k, v in cookie.items()}
        
        # Get the session key
        session_key = cookies.get('sessionid')
        
        # Set the user in the scope
        if session_key:
            scope['user'] = await get_user(session_key)
        else:
            scope['user'] = AnonymousUser()
        
        # Store cookies in scope for convenience
        scope['cookies'] = cookies
            
        # Continue processing
        return await super().__call__(scope, receive, send)
