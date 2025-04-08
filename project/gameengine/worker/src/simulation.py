import asyncio
import json
import datetime
from channels.layers import get_channel_layer
from channels.consumer import AsyncConsumer
from gameengine.src.channel_groups import get_game_group_name


class SimulationConsumer(AsyncConsumer):
    """Consumer that handles simulation commands and updates"""

    # This will be our in-memory state for each game
    simulations = {}
    update_tasks = {}

    async def start_simulation(self, event):
        """Start the simulation if it's not already running"""
        game_id = event.get('game_id')
        if not game_id:
            print("Error: No game_id provided")
            return

        if game_id not in self.simulations:
            self.simulations[game_id] = {
                'entities': {},
                'time': 0,
                'last_update': str(datetime.datetime.now()),
                'game_id': game_id,
                'settings': event.get('settings', {})
            }

        if game_id not in self.update_tasks or self.update_tasks[game_id].done():
            self.update_tasks[game_id] = asyncio.create_task(self.run_simulation(game_id))
            print(f"Simulation started for game {game_id}")

    async def stop_simulation(self, event):
        """Stop the simulation if it's running"""
        game_id = event.get('game_id')
        if not game_id:
            print("Error: No game_id provided")
            return

        if game_id in self.update_tasks and not self.update_tasks[game_id].done():
            self.update_tasks[game_id].cancel()
            try:
                await self.update_tasks[game_id]
            except asyncio.CancelledError:
                pass
            del self.update_tasks[game_id]
            print(f"Simulation stopped for game {game_id}")

    async def update_entity(self, event):
        """Update an entity in the simulation"""
        game_id = event.get('game_id')
        entity_id = event.get('entity_id')
        entity_data = event.get('entity_data', {})
        
        if not game_id or not entity_id:
            print("Error: Missing game_id or entity_id")
            return
            
        if game_id not in self.simulations:
            print(f"Error: Game {game_id} not found")
            return
            
        self.simulations[game_id]['entities'][entity_id] = entity_data
        print(f"Updated entity {entity_id} in game {game_id}")

    async def update_settings(self, event):
        """Update simulation settings"""
        game_id = event.get('game_id')
        settings = event.get('settings', {})
        
        if not game_id:
            print("Error: No game_id provided")
            return
            
        if game_id not in self.simulations:
            print(f"Error: Game {game_id} not found")
            return
            
        self.simulations[game_id]['settings'] = settings
        print(f"Updated settings for game {game_id}")

    async def run_simulation(self, game_id):
        """Run the simulation loop - our long-running process"""
        channel_layer = get_channel_layer()
        game_group = get_game_group_name(game_id)
        
        try:
            while True:
                # Get the simulation state for this game
                sim_state = self.simulations[game_id]
                
                # Update simulation time
                sim_state['time'] += 1
                sim_state['last_update'] = str(datetime.datetime.now())

                # Update entities based on simulation rules
                for entity_id, entity in list(sim_state['entities'].items()):
                    # Example: move entities
                    if 'position' in entity and 'velocity' in entity:
                        entity['position'] = [
                            entity['position'][0] + entity['velocity'][0],
                            entity['position'][1] + entity['velocity'][1]
                        ]

                # Report state periodically
                if sim_state['time'] % 10 == 0:  # Every 10 time steps
                    await channel_layer.group_send(
                        game_group,
                        {
                            'type': 'game_state',
                            'message_type': 'game_state',
                            'game_state': {
                                'status': 'active',
                                'resources': {
                                    'lives': sim_state.get('settings', {}).get('lives', 10),
                                    'money': sim_state.get('settings', {}).get('money', 100),
                                    'score': sim_state['time'] * 10  # Example score calculation
                                },
                                'wave': sim_state['time'] // 100 + 1,
                                'time_remaining': 300 - (sim_state['time'] % 300)
                            },
                            'timestamp': sim_state['last_update']
                        }
                    )
                    
                    # Also send elements update
                    if sim_state['entities']:
                        await channel_layer.group_send(
                            game_group,
                            {
                                'type': 'elems_update',
                                'message_type': 'elems_update',
                                'list_items': [
                                    {
                                        'id': entity_id,
                                        'type': entity.get('type', 'unknown'),
                                        'position': entity.get('position', [0, 0]),
                                        'state': entity.get('state', 'active'),
                                        'properties': entity.get('properties', {})
                                    }
                                    for entity_id, entity in sim_state['entities'].items()
                                ],
                                'timestamp': sim_state['last_update']
                            }
                        )
                    
                    print(f"Reported state for game {game_id} at time {sim_state['time']}")

                # Sleep to control simulation speed
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print(f"Simulation loop cancelled for game {game_id}")
            raise
        except Exception as e:
            print(f"Error in simulation loop for game {game_id}: {e}")
            # Remove the task from our tracking
            if game_id in self.update_tasks:
                del self.update_tasks[game_id]
