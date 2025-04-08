"""
API URL configuration for gameengine app.
"""
from django.urls import path
from project.gameengine.gameengine import v1_views

urlpatterns = [
    path('trigger-websocket/', v1_views.TriggerWebSocketView.as_view(), name='trigger_websocket'),
    path('game-types/', v1_views.GameTypesView.as_view(), name='game_types'),
    path('game-instances/', v1_views.GameInstancesView.as_view(), name='game_instances'),
    path('game-instances/<uuid:game_id>/', v1_views.GameInstanceDetailView.as_view(), name='game_instance_detail'),
    path('game-instances/<uuid:game_id>/join/', v1_views.JoinGameView.as_view(), name='join_game'),
    path('game-instances/<uuid:game_id>/start/', v1_views.StartGameView.as_view(), name='start_game'),
    path('game-instances/<uuid:game_id>/settings/', v1_views.UpdateGameSettingsView.as_view(), name='update_game_settings'),
]
