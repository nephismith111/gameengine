from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('<uuid:game_id>/', login_required(views.waiting_room_view), name='waiting_room'),
]
