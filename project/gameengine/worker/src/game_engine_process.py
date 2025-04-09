"""
Game Engine Process - Main worker process that polls for ready games and starts game subprocesses
"""
import time
import logging
import importlib
from uuid import UUID
from typing import Dict, Any, Optional

from django.conf import settings

from gameengine.project_settings import WORKER_POLL_SECONDS
from gameengine.src.games import update_game_status
from gameengine.exceptions import GameEngineError
from gameengine.models import GameInstance
logger = logging.getLogger(__name__)

# Dictionary to track running game processes
# Key: game_id (UUID), Value: game process object
running_games = {}

class GameEngineProcess:
    """
    Main game engine process that polls the database for games in READY state
    and starts appropriate game subprocesses.
    """
    
    def __init__(self):
        self.poll_interval = WORKER_POLL_SECONDS
        self.running = True
        logger.info("Game Engine Process initialized with poll interval: %s seconds", self.poll_interval)
    
    def start(self):
        """Start the main game engine process loop"""
        logger.info("Starting Game Engine Process")
        
        try:
            while self.running:
                # Poll for ready games
                ready_games = self._poll_for_ready_games()
                
                # Start ready games
                self._start_ready_games(ready_games)
                
                # Check status of running games
                self._check_running_games()
                
                # Sleep for the configured interval
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logger.info("Game Engine Process stopped by user")
        except Exception as e:
            logger.exception("Error in Game Engine Process: %s", str(e))
        finally:
            self._cleanup()
    
    def stop(self):
        """Stop the game engine process"""
        logger.info("Stopping Game Engine Process")
        self.running = False
        self._cleanup()
    
    def _poll_for_ready_games(self):
        """Poll the database for games in READY state
        
        Returns:
            list: List of ready games
        """
        try:
            # Query for games in READY state
            ready_games = self._get_ready_games()
            return ready_games
        except Exception as e:
            logger.exception("Error polling for ready games: %s", str(e))
            return []
    
    def _start_ready_games(self, ready_games: list):
        """Start game subprocesses for all ready games that aren't already running"""
        try:
            for game in ready_games:
                game_id = game['id']
                game_type = game['game_type']['id']
                
                # Start the game if it's not already running
                if str(game_id) not in running_games:
                    self._start_game_subprocess(game_id, game_type, game)
        except Exception as e:
            logger.exception("Error starting ready games: %s", str(e))
    
    def _get_ready_games(self) -> list:
        """
        Query the database for games in READY state
        Returns a list of game instances
        """
        # This is a placeholder for actual database query
        # In a real implementation, you would use Django ORM

        
        ready_games = []
        try:
            # Get all game instances with status 'ready'
            game_instances = GameInstance.objects.filter(status='ready')
            
            for instance in game_instances:
                # Format the game instance data
                game_data = {
                    'id': instance.id,
                    'game_type': {
                        'id': instance.game_type.id,
                        'name': instance.game_type.name
                    },
                    'instance_name': instance.instance_name,
                    'game_settings': instance.game_data.get('game_settings', {})
                }
                ready_games.append(game_data)
                
                # Update the game status to 'starting'
                update_game_status(instance.id, 'starting')
                
        except Exception as e:
            logger.exception("Error getting ready games: %s", str(e))
        
        return ready_games
    
    def _start_game_subprocess(self, game_id: UUID, game_type_id: int, game_data: Dict[str, Any]):
        """Start a game subprocess for the specified game"""
        try:
            logger.info(f"Starting game subprocess for game_id: {game_id}, type: {game_type_id}")
            
            # Determine which game module to load based on game_type_id
            game_module = self._get_game_module(game_type_id)
            
            if not game_module:
                logger.error(f"No game module found for game type: {game_type_id}")
                return
            
            # Import the game module dynamically
            try:
                module = importlib.import_module(f"worker.src.games.{game_module}")
                game_class = getattr(module, "GameProcess")
                
                # Create and start the game process
                game_process = game_class(game_id, game_data)
                game_process.start()
                
                # Store the running game process
                running_games[str(game_id)] = game_process
                
                logger.info(f"Game subprocess started for game_id: {game_id}")
                
            except (ImportError, AttributeError) as e:
                logger.exception(f"Error importing game module {game_module}: {str(e)}")
                # Update game status to 'error'
                update_game_status(game_id, 'error')
                
        except Exception as e:
            logger.exception(f"Error starting game subprocess: {str(e)}")
            # Update game status to 'error'
            update_game_status(game_id, 'error')
    
    def _get_game_module(self, game_type_id: int) -> Optional[str]:
        """
        Map game_type_id to the appropriate game module
        Returns the module name or None if not found
        """
        # This is a simple switch case implementation using a dictionary
        game_modules = {
            1: "tower_defense",
            2: "resource_management",
            3: "puzzle_game",
            # Add more game types as needed
        }
        
        return game_modules.get(game_type_id)
    
    def _check_running_games(self):
        """Check the status of running games and clean up completed ones"""
        games_to_remove = []
        
        for game_id, game_process in running_games.items():
            # Check if the game is still running
            if not game_process.is_running():
                logger.info(f"Game {game_id} has completed")
                games_to_remove.append(game_id)
        
        # Remove completed games
        for game_id in games_to_remove:
            del running_games[game_id]
    
    def _cleanup(self):
        """Clean up resources when stopping the process"""
        logger.info("Cleaning up Game Engine Process resources")
        
        # Stop all running games
        for game_id, game_process in running_games.items():
            try:
                logger.info(f"Stopping game {game_id}")
                game_process.stop()
            except Exception as e:
                logger.error(f"Error stopping game {game_id}: {str(e)}")
        
        # Clear the running games dictionary
        running_games.clear()
        
        # No need to manually close database connections - Django handles this
