"""
Tower Defense Game Process - Implementation of tower defense game logic
"""
import logging
import time
import random
from uuid import UUID
from typing import Dict, Any, List

from worker.src.games.base_game import BaseGameProcess
from gameengine.src.websocket_messaging import send_elements_update, send_game_state_update

logger = logging.getLogger(__name__)

class GameProcess(BaseGameProcess):
    """
    Tower Defense game implementation.
    This is a simple example implementation that simulates a tower defense game.
    """
    
    def __init__(self, game_id: UUID, game_data: Dict[str, Any]):
        super().__init__(game_id, game_data)
        # Tower defense specific variables
        self.towers = []
        self.enemies = []
        self.wave_timer = 0
        self.wave_interval = self.game_settings.get('wave_interval', 30)  # seconds between waves
        self.max_waves = self.game_settings.get('max_waves', 10)
        
        # Extend the base game state with tower defense specific state
        self.game_state.update({
            'resources': {
                'lives': self.game_settings.get('starting_lives', 20),
                'money': self.game_settings.get('starting_money', 100),
                'score': 0
            },
            'wave': 0,  # Current wave number
            'time_remaining': self.wave_interval,
            'progress': 0  # Will be calculated as current_wave / max_waves
        })
        
        logger.info(f"Initialized Tower Defense game {self.game_id} with wave interval: {self.wave_interval}s")
    
    def _initialize_game(self):
        """Initialize the tower defense game state"""
        logger.info(f"Initializing Tower Defense game {self.game_id}")
        
        # Game state is already initialized in __init__
        # Just send initial elements update (empty at start)
        self._send_elements_update()
    
    def _process_game_tick(self, user_inputs: Dict[int, Dict[str, Any]]):
        """
        Process a single game tick for tower defense
        
        Args:
            user_inputs: Dictionary of user inputs by user_id
        """
        # Process user inputs (e.g., tower placement, upgrades)
        self._process_user_inputs(user_inputs)
        
        # Update wave timer based on the game tick rate
        self.wave_timer += self.game_tick_rate
        self.game_state['time_remaining'] = max(0, self.wave_interval - (self.wave_timer % self.wave_interval))
        
        # Check if it's time for a new wave
        if self.wave_timer >= self.wave_interval:
            self.wave_timer = 0
            self._start_new_wave()
        
        # Process enemy movement
        self._move_enemies()
        
        # Process tower attacks
        self._process_tower_attacks()
        
        # Update progress indicator (for UI progress bars, etc.)
        if self.max_waves > 0:
            self.game_state['progress'] = min(100, int((self.game_state['wave'] / self.max_waves) * 100))
        
        # Check game end conditions
        self._check_game_end_conditions()
        
        # Send elements update based on frames_per_second
        # This is now handled by the base class's update interval logic
        current_time = time.time()
        time_since_last_update = current_time - self.last_update_time
        
        if time_since_last_update >= self.update_interval:
            self._send_elements_update()
    
    def _start_new_wave(self):
        """Start a new wave of enemies"""
        self.game_state['wave'] += 1
        wave_num = self.game_state['wave']
        
        logger.info(f"Starting wave {wave_num} for game {self.game_id}")
        
        # Don't spawn more waves if we've reached the maximum
        if wave_num > self.max_waves:
            if self.game_state['status'] != 'won':
                self.game_state['status'] = 'won'
                logger.info(f"Game {self.game_id} won - all waves completed")
            return
        
        # Spawn enemies based on wave number
        num_enemies = 5 + (wave_num * 2)  # More enemies each wave
        
        for i in range(num_enemies):
            enemy = {
                'id': f"enemy_{wave_num}_{i}",
                'type': 'enemy',
                'position': {'x': 0, 'y': random.randint(50, 450)},
                'state': 'active',
                'properties': {
                    'health': 50 + (wave_num * 10),
                    'speed': 2 + (wave_num * 0.2),
                    'value': 10 + wave_num
                }
            }
            self.enemies.append(enemy)
    
    def _move_enemies(self):
        """Move all active enemies"""
        enemies_to_remove = []
        
        for enemy in self.enemies:
            if enemy['state'] != 'active':
                continue
                
            # Move enemy to the right
            enemy['position']['x'] += enemy['properties']['speed']
            
            # Check if enemy reached the end
            if enemy['position']['x'] > 800:  # Assuming 800px is the right edge
                # Player loses a life
                self.game_state['resources']['lives'] -= 1
                enemies_to_remove.append(enemy)
        
        # Remove enemies that reached the end
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)
    
    def _process_tower_attacks(self):
        """Process tower attacks on enemies"""
        for tower in self.towers:
            if tower['state'] != 'active':
                continue
                
            # Find closest enemy in range
            target = self._find_target_for_tower(tower)
            
            if target:
                # Attack the enemy
                damage = tower['properties'].get('damage', 10)
                target['properties']['health'] -= damage
                
                # Check if enemy is defeated
                if target['properties']['health'] <= 0:
                    target['state'] = 'defeated'
                    
                    # Award money and score
                    self.game_state['resources']['money'] += target['properties']['value']
                    self.game_state['resources']['score'] += target['properties']['value']
                    
                    # Remove defeated enemy
                    self.enemies.remove(target)
    
    def _find_target_for_tower(self, tower):
        """Find the closest enemy in range for a tower"""
        tower_range = tower['properties'].get('range', 100)
        tower_x = tower['position']['x']
        tower_y = tower['position']['y']
        
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in self.enemies:
            if enemy['state'] != 'active':
                continue
                
            enemy_x = enemy['position']['x']
            enemy_y = enemy['position']['y']
            
            # Calculate distance
            distance = ((tower_x - enemy_x) ** 2 + (tower_y - enemy_y) ** 2) ** 0.5
            
            if distance <= tower_range and distance < closest_distance:
                closest_enemy = enemy
                closest_distance = distance
        
        return closest_enemy
    
    def _check_game_end_conditions(self):
        """Check if the game has ended"""
        # Check if player has lost all lives
        if self.game_state['resources']['lives'] <= 0:
            self.game_state['status'] = 'lost'
            logger.info(f"Game {self.game_id} lost - no lives remaining")
            self.running = False
        
        # Check if all waves are complete and no enemies left
        if self.game_state['wave'] >= self.max_waves and not self.enemies:
            self.game_state['status'] = 'won'
            logger.info(f"Game {self.game_id} won - all waves completed")
            self.running = False
    
    def _process_user_inputs(self, user_inputs: Dict[int, Dict[str, Any]]):
        """
        Process user inputs for tower defense
        
        Args:
            user_inputs: Dictionary of user inputs by user_id
        """
        for user_id, inputs in user_inputs.items():
            # Process tower placement
            if 'place_tower' in inputs:
                tower_data = inputs['place_tower']
                self._place_tower(user_id, tower_data)
            
            # Process tower upgrades
            if 'upgrade_tower' in inputs:
                tower_id = inputs['upgrade_tower']
                self._upgrade_tower(user_id, tower_id)
            
            # Process tower selling
            if 'sell_tower' in inputs:
                tower_id = inputs['sell_tower']
                self._sell_tower(user_id, tower_id)
    
    def _place_tower(self, user_id: int, tower_data: Dict[str, Any]):
        """Place a new tower"""
        # Check if the user has enough money
        tower_cost = tower_data.get('cost', 50)
        if self.game_state['resources']['money'] >= tower_cost:
            # Create a new tower
            tower_id = f"tower_{len(self.towers) + 1}"
            tower = {
                'id': tower_id,
                'type': 'tower',
                'position': tower_data.get('position', {'x': 0, 'y': 0}),
                'state': 'active',
                'owner_id': user_id,
                'properties': {
                    'damage': tower_data.get('damage', 10),
                    'range': tower_data.get('range', 100),
                    'fire_rate': tower_data.get('fire_rate', 1.0),
                    'level': 1
                }
            }
            
            # Add the tower to the game
            self.towers.append(tower)
            
            # Deduct the cost from the player's money
            self.game_state['resources']['money'] -= tower_cost
            
            logger.info(f"User {user_id} placed tower {tower_id} in game {self.game_id}")
    
    def _upgrade_tower(self, user_id: int, tower_id: str):
        """Upgrade an existing tower"""
        # Find the tower
        for tower in self.towers:
            if tower['id'] == tower_id and tower['owner_id'] == user_id:
                # Calculate upgrade cost (increases with level)
                upgrade_cost = 25 * tower['properties']['level']
                
                # Check if the user has enough money
                if self.game_state['resources']['money'] >= upgrade_cost:
                    # Upgrade the tower
                    tower['properties']['level'] += 1
                    tower['properties']['damage'] *= 1.5  # 50% damage increase
                    tower['properties']['range'] *= 1.2   # 20% range increase
                    
                    # Deduct the cost from the player's money
                    self.game_state['resources']['money'] -= upgrade_cost
                    
                    logger.info(f"User {user_id} upgraded tower {tower_id} to level {tower['properties']['level']} in game {self.game_id}")
                break
    
    def _sell_tower(self, user_id: int, tower_id: str):
        """Sell an existing tower"""
        # Find the tower
        for i, tower in enumerate(self.towers):
            if tower['id'] == tower_id and tower['owner_id'] == user_id:
                # Calculate sell value (50% of total investment)
                base_cost = 50  # Base tower cost
                upgrade_costs = sum(25 * level for level in range(1, tower['properties']['level']))
                sell_value = int((base_cost + upgrade_costs) * 0.5)
                
                # Remove the tower
                self.towers.pop(i)
                
                # Add the sell value to the player's money
                self.game_state['resources']['money'] += sell_value
                
                logger.info(f"User {user_id} sold tower {tower_id} for {sell_value} in game {self.game_id}")
                break
    
    def _send_elements_update(self):
        """Send game elements update to clients via WebSocket"""
        try:
            # Combine towers and enemies into a single list
            elements = self.towers + [e for e in self.enemies if e['state'] == 'active']
            
            # Send the update
            send_elements_update(self.game_id, elements)
        except Exception as e:
            logger.error(f"Error sending elements update for {self.game_id}: {str(e)}")
    
    def _send_game_state_update(self):
        """
        Override the base method to send tower defense specific state updates
        that include wave information instead of generic progress.
        """
        try:
            send_game_state_update(
                self.game_id,
                self.game_state['status'],
                self.game_state['resources'],
                self.game_state['wave'],  # Send wave instead of generic progress
                self.game_state.get('time_remaining')
            )
        except Exception as e:
            logger.error(f"Error sending game state update for {self.game_id}: {str(e)}")
