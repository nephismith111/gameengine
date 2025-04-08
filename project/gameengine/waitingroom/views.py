from django.shortcuts import render, get_object_or_404
from gameengine.models import GameInstance


def waiting_room_view(request, game_id):
    """
    View for the game waiting room.
    """
    # We don't need to fetch the game instance here as it will be loaded via JavaScript
    return render(request, 'waitingroom/waiting_room.html', {'game_id': game_id})
