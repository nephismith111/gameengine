"""
API URL configuration for gameengine app.
"""
from django.urls import path
from project.gameengine.gameengine import v1_views

urlpatterns = [
    path('trigger-websocket/', v1_views.TriggerWebSocketView.as_view(), name='trigger_websocket'),
]
