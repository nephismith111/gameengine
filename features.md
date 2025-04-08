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

## API Endpoints

- `/gameengine/v1/game-types/` - List all game types
- `/gameengine/v1/game-instances/` - List all game instances or create a new one
- `/gameengine/v1/game-instances/<uuid:game_id>/` - Get details of a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/join/` - Join a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/start/` - Start a specific game instance
- `/gameengine/v1/trigger-websocket/` - Trigger a WebSocket message (for testing)

## WebSocket Functionality

- Validation messages
- Elements update messages (for game element updates)
- Game state messages (for game status and resource updates)

## User Interface

- Welcome page with game tiles and game instances table
- Waiting room with player list and game controls
- Game creator controls

## JavaScript Module Organization

- `gameengine_root.js` - Main entry point and initialization
- `api_urls.js` - API URL definitions
- `websocket_client.js` - WebSocket client implementation
- `game_types.js` - Game type loading and rendering
- `game_instances.js` - Game instance loading and rendering
- `utils.js` - Utility functions

## Testing Status

| Feature | Test Coverage | Notes |
|---------|--------------|-------|
| User Authentication | Partial | Basic login/logout tested |
| Game Type Listing | Minimal | |
| Game Instance Creation | Minimal | |
| Game Instance Joining | Minimal | |
| Waiting Room | Minimal | |
| WebSocket Communication | Minimal | Only validation tested |
