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


@method_decorator(csrf_exempt, name='dispatch')
class GameTypesView(LoginRequiredMixin, View):
    """
    API endpoint to get all game types.
    """
    def get(self, request, *args, **kwargs):
        from gameengine.src.games import get_all_game_types
        
        game_types = get_all_game_types()
        return JsonResponse({'game_types': game_types})
    
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class GameInstancesView(LoginRequiredMixin, View):
    """
    API endpoint to get all game instances or create a new one.
    """
    def get(self, request, *args, **kwargs):
        from gameengine.src.games import get_all_game_instances
        
        game_instances = get_all_game_instances()
        return JsonResponse({'game_instances': game_instances})
    
    def post(self, request, *args, **kwargs):
        from gameengine.src.games import create_game_instance
        
        try:
            data = json.loads(request.body)
            game_type_id = data.get('game_type_id')
            instance_name = data.get('instance_name')
            
            if not game_type_id or not instance_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)
            
            game_instance = create_game_instance(
                game_type_id=game_type_id,
                instance_name=instance_name,
                user=request.user
            )
            
            return JsonResponse(game_instance, status=201)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class GameInstanceDetailView(LoginRequiredMixin, View):
    """
    API endpoint to get details of a specific game instance.
    """
    def get(self, request, game_id, *args, **kwargs):
        from gameengine.src.games import get_game_instance
        
        try:
            game_instance = get_game_instance(game_id)
            return JsonResponse(game_instance)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=404)
    
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class JoinGameView(LoginRequiredMixin, View):
    """
    API endpoint to join a game instance.
    """
    def post(self, request, game_id, *args, **kwargs):
        from gameengine.src.games import join_game_instance
        
        try:
            game_instance = join_game_instance(game_id, request.user)
            return JsonResponse(game_instance)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class StartGameView(LoginRequiredMixin, View):
    """
    API endpoint to start a game instance.
    """
    def post(self, request, game_id, *args, **kwargs):
        from gameengine.src.games import start_game_instance
        
        try:
            game_instance = start_game_instance(game_id, request.user)
            return JsonResponse(game_instance)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)


