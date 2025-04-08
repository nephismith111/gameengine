"""
WebSocket URL configuration for gameengine project.
"""
from django.urls import re_path
from project.gameengine.gameengine.consumers import ValidateConsumer

websocket_urlpatterns = [
    # Define WebSocket URL patterns here
    re_path(r'ws/validate/$', ValidateConsumer.as_asgi()),
]
