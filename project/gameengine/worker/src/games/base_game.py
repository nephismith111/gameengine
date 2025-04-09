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
        
        # Configure game tick rate and update frequency
        self.game_tick_rate = self.game_settings.get('game_tick_rate', 0.1)  # Default: 10 ticks per second
        self.frames_per_second = self.game_settings.get('frames_per_second', 10)  # Default: 10 FPS
        self.update_interval = 1.0 / self.frames_per_second if self.frames_per_second > 0 else 0.1
        
        # Track time for update frequency
        self.last_update_time = 0
        
        # User input tracking
        self.user_inputs = {}  # Dictionary to store user inputs by user_id
        self.input_lock = threading.Lock()  # Lock for thread-safe access to user_inputs
        
        self.game_state = {
            'status': 'initializing',
            # Game-specific state should be added by subclasses
        }
        
        logger.info(f"Initialized BaseGameProcess for game {self.game_id} with tick rate: {self.game_tick_rate}s, update interval: {self.update_interval}s")
    
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
            
            # Track time for update frequency
            self.last_update_time = time.time()
            
            # Run the game loop until stopped
            while self.running:
                loop_start_time = time.time()
                
                # Get user inputs for this tick
                user_inputs = self._get_user_inputs()
                
                # Process game logic with user inputs
                self._process_game_tick(user_inputs)
                
                # Send updates to clients based on frames_per_second setting
                current_time = time.time()
                time_since_last_update = current_time - self.last_update_time
                
                if time_since_last_update >= self.update_interval:
                    self._send_game_state_update()
                    self.last_update_time = current_time
                
                # Calculate how long to sleep to maintain the desired tick rate
                processing_time = time.time() - loop_start_time
                sleep_time = max(0, self.game_tick_rate - processing_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
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
    
    def _process_game_tick(self, user_inputs: Dict[int, Dict[str, Any]]):
        """
        Process a single game tick - to be implemented by subclasses
        
        Args:
            user_inputs: Dictionary of user inputs by user_id
        """
        raise NotImplementedError("Subclasses must implement _process_game_tick")
    
    def _get_user_inputs(self):
        """
        Get user inputs for the current game tick.
        This is a stub that would be replaced with actual Redis pubsub implementation.
        
        Returns:
            dict: Dictionary of user inputs by user_id
        """
        try:
            # This is a stub implementation
            # In a real implementation, this would fetch inputs from Redis pubsub
            # or another message queue system
            
            # For now, just return the current user_inputs dictionary
            with self.input_lock:
                # Return a copy to avoid modification during iteration
                return self.user_inputs.copy()
        except Exception as e:
            logger.error(f"Error getting user inputs for game {self.game_id}: {str(e)}")
            return {}
    
    def process_user_input(self, user_id: int, input_data: Dict[str, Any]):
        """
        Process user input received from client.
        This method would be called when input is received from Redis pubsub.
        
        Args:
            user_id: ID of the user who sent the input
            input_data: Dictionary containing input data (keys, mouse, etc.)
        """
        try:
            with self.input_lock:
                # Store the input data for the user
                if user_id not in self.user_inputs:
                    self.user_inputs[user_id] = {}
                
                # Update the user's input data
                # This might include key states, mouse position, button clicks, etc.
                self.user_inputs[user_id].update(input_data)
                
                # Handle key up events by removing keys that are no longer pressed
                if 'key_up' in input_data:
                    for key in input_data['key_up']:
                        if 'keys' in self.user_inputs[user_id] and key in self.user_inputs[user_id]['keys']:
                            self.user_inputs[user_id]['keys'].remove(key)
                
                logger.debug(f"Processed input from user {user_id} for game {self.game_id}: {input_data}")
        except Exception as e:
            logger.error(f"Error processing user input for game {self.game_id}, user {user_id}: {str(e)}")
    
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
