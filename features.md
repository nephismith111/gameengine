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
- Waiting room update messages - Used for comprehensive waiting room state updates including player lists

## Known Issues

- TODO: Fix notification not showing up on remote browsers in waiting room
  - The WebSocket update is received but notifications don't appear
  - Settings are correctly updated in the UI

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
- **Game Engine Process**: Polls database for ready games and starts game subprocesses
- **Management Command**: `run_game_engine` starts the worker process
- **Docker Service**: Dedicated container for running the worker process

### Worker Features

- Polls database for games in "ready" state
- Starts appropriate game subprocess based on game type
- Maintains in-memory game state for multiple simultaneous games
- Processes game logic in a continuous loop
- Sends periodic updates to connected clients via WebSockets
- Handles entity creation, updates, and game state changes

### Game Process Architecture

- **BaseGameProcess**: Abstract base class for all game types
- **Game-Specific Implementations**: Each game type has its own implementation
- **Game States**:
  - `ready`: Game is ready to start but not yet running
  - `starting`: Game is in the process of starting
  - `ongoing`: Game is actively running
  - `ended`: Game has completed
  - `error`: Game encountered an error

### Worker Communication

- **Database Polling**: Checks for games in "ready" state at regular intervals
- **Output Channels**: Sends updates to game-specific WebSocket groups
- **Message Types**:
  - `game_state`: Updates overall game state (status, resources, wave)
  - `elems_update`: Updates game elements (towers, enemies, etc.)

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
