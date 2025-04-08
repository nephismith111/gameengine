"""
API views for the gameengine app.
"""
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json

# Import the WebSocket messaging functionality
from project.gameengine.gameengine.src.websocket_messaging import send_validation_message

@method_decorator(csrf_exempt, name='dispatch')
class TriggerWebSocketView(LoginRequiredMixin, View):
    """
    API endpoint to trigger a WebSocket message.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to trigger a WebSocket message.
        """
        # Call the function to send a WebSocket message
        send_validation_message(request.user.id)
        
        return JsonResponse({
            'status': 'success',
            'message': 'WebSocket message triggered'
        })
    
    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        Handle methods other than POST.
        """
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST requests are allowed'
        }, status=405)
