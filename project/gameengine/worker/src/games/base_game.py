"""
Base Game Process - Abstract base class for all game processes
"""
import logging
import threading
import time
from uuid import UUID
from typing import Dict, Any, Optional

from gameengine.src.games import update_game_status
from gameengine.src.websocket_messaging import send_game_state_update

logger = logging.getLogger(__name__)

class BaseGameProcess:
    """
    Abstract base class for all game processes.
    Each specific game type should inherit from this class and implement
    the required methods.
    
    Game implementations must override:
    - _initialize_game(): Set up initial game state
    - _process_game_tick(): Process a single game tick
    
    Game state is unique to each game type and should be defined in the
    game's implementation. The base class provides a minimal structure
    that can be extended as needed.
    """
    
    def __init__(self, game_id: UUID, game_data: Dict[str, Any]):
        self.game_id = game_id
        self.game_data = game_data
        self.game_settings = game_data.get('game_settings', {})
        self.instance_name = game_data.get('instance_name', 'Unknown Game')
        self.running = False
        self.thread = None
        self.game_state = {
            'status': 'initializing',
            # Game-specific state should be added by subclasses
        }
        logger.info(f"Initialized BaseGameProcess for game {self.game_id}")
    
    def start(self):
        """Start the game process in a separate thread"""
        if self.running:
            logger.warning(f"Game {self.game_id} is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_game_loop)
        self.thread.daemon = True  # Make thread a daemon so it exits when main process exits
        self.thread.start()
        
        # Update game status in database
        update_game_status(self.game_id, 'ongoing')
        logger.info(f"Started game process for {self.game_id}")
    
    def stop(self):
        """Stop the game process"""
        logger.info(f"Stopping game {self.game_id}")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            # Wait for the thread to finish
            self.thread.join(timeout=5.0)
            
        # Update game status in database
        update_game_status(self.game_id, 'ended')
        logger.info(f"Game {self.game_id} stopped")
    
    def is_running(self) -> bool:
        """Check if the game is still running"""
        if not self.running:
            return False
        
        if self.thread and not self.thread.is_alive():
            self.running = False
            return False
            
        return True
    
    def _run_game_loop(self):
        """Main game loop - to be implemented by subclasses"""
        try:
            # Initialize the game
            self._initialize_game()
            
            # Update game status
            self.game_state['status'] = 'active'
            self._send_game_state_update()
            
            # Run the game loop until stopped
            while self.running:
                # Process game logic
                self._process_game_tick()
                
                # Send updates to clients
                self._send_game_state_update()
                
                # Sleep for a short time
                time.sleep(0.1)  # 100ms tick rate
                
        except Exception as e:
            logger.exception(f"Error in game loop for {self.game_id}: {str(e)}")
            self.game_state['status'] = 'error'
            self._send_game_state_update()
        finally:
            # Ensure game status is updated when the loop exits
            if self.game_state['status'] not in ['won', 'lost', 'error']:
                self.game_state['status'] = 'ended'
            
            self._send_game_state_update()
            update_game_status(self.game_id, 'ended')
    
    def _initialize_game(self):
        """Initialize the game state - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _initialize_game")
    
    def _process_game_tick(self):
        """Process a single game tick - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _process_game_tick")
    
    def _send_game_state_update(self):
        """
        Send game state update to clients via WebSocket.
        
        This is a basic implementation that sends the minimal required fields.
        Game implementations should override this method if they need to send
        additional or different state information.
        """
        try:
            # Extract common fields with safe defaults
            status = self.game_state.get('status', 'active')
            resources = self.game_state.get('resources', {})
            progress = self.game_state.get('progress', 0)  # Generic progress indicator
            time_remaining = self.game_state.get('time_remaining')
            
            send_game_state_update(
                self.game_id,
                status,
                resources,
                progress,
                time_remaining
            )
        except Exception as e:
            logger.error(f"Error sending game state update for {self.game_id}: {str(e)}")
