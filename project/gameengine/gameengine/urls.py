"""
URL configuration for gameengine project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    # User authentication URLs
    path('auth/', include('userauth.urls')),
    # Main app URLs
    path('', login_required(TemplateView.as_view(template_name='gameengine/index.html')), name='home'),
    # Waiting room URLs
    path('waitingroom/', include('waitingroom.urls')),
    # API URLs from gameengine app
    path('gameengine/v1/', include('gameengine.v1_urls')),
    # API URLs will be included from each app's v1_urls.py
]
