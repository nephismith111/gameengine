# Game Engine Features

This document tracks the features of the Game Engine application to help with designing and maintaining tests.

## Core Features

- User authentication (login, registration, logout)
- Game type listing and selection
- Game instance creation
- Game instance joining
- Waiting room functionality
- Game starting mechanism
- WebSocket communication for real-time updates
- Long-running simulation worker for game state management

## API Endpoints

- `/gameengine/v1/game-types/` - List all game types
- `/gameengine/v1/game-instances/` - List all game instances or create a new one
- `/gameengine/v1/game-instances/<uuid:game_id>/` - Get details of a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/join/` - Join a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/start/` - Start a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/settings/` - Update settings for a specific game instance
- `/gameengine/v1/trigger-websocket/` - Trigger a WebSocket message (for testing)

## WebSocket Functionality

- Validation messages
- Elements update messages (for game element updates) - Used for real-time updates of game elements
- Game state messages (for game status and resource updates) - Used for real-time game state changes
- Settings update messages (for game settings changes in waiting room) - Note: Consider moving to AJAX responses

## User Interface

- Welcome page with game tiles and game instances table
- Waiting room with player list, game settings editor, and game controls
- Game creator controls

## JavaScript Module Organization

- `gameengine_root.js` - Main entry point and initialization
- `api_urls.js` - API URL definitions
- `websocket_client.js` - WebSocket client implementation
- `game_types.js` - Game type loading and rendering
- `game_instances.js` - Game instance loading and rendering
- `utils.js` - Utility functions

## Worker Process

The game engine includes a long-running worker process that manages game simulations:

- **Worker App**: Django app that contains the simulation worker code
- **Simulation Consumer**: Handles simulation commands and updates game state
- **Management Command**: `run_simulation_worker` starts the worker process
- **Docker Service**: Dedicated container for running the worker process

### Worker Features

- Maintains in-memory game state for multiple simultaneous games
- Processes game logic in a continuous loop
- Sends periodic updates to connected clients via WebSockets
- Responds to commands from the main application
- Handles entity creation, updates, and game state changes

### Worker Communication

- **Input Channel**: Listens on the "simulation" channel for commands
- **Output Channels**: Sends updates to game-specific WebSocket groups
- **Message Types**:
  - `start_simulation`: Begins a new simulation for a game
  - `stop_simulation`: Stops an ongoing simulation
  - `update_entity`: Updates an entity in the simulation
  - `update_settings`: Updates simulation settings

## Testing Status

| Feature | Test Coverage | Notes |
|---------|--------------|-------|
| User Authentication | Partial | Basic login/logout tested |
| Game Type Listing | Minimal | |
| Game Instance Creation | Minimal | |
| Game Instance Joining | Minimal | |
| Waiting Room | Minimal | |
| WebSocket Communication | Minimal | Only validation tested |
| Simulation Worker | None | New feature |
