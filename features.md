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

## Game Types

- Tower Defense
  - Description: Defend your base by strategically placing towers to stop enemies
  - Status: Implemented
  - Tests: Basic tests implemented

## API Endpoints

- `/gameengine/v1/game-types/` - List all game types
- `/gameengine/v1/game-instances/` - List all game instances or create a new one
- `/gameengine/v1/game-instances/<uuid:game_id>/` - Get details of a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/join/` - Join a specific game instance
- `/gameengine/v1/game-instances/<uuid:game_id>/start/` - Start a specific game instance
- `/gameengine/v1/trigger-websocket/` - Trigger a WebSocket message (for testing)

## WebSocket Functionality

- Validation messages
- Game state updates
- Player join/leave notifications

## User Interface

- Welcome page with game tiles and game instances table
- Waiting room with player list and game controls
- Game creator controls

## Testing Status

| Feature | Test Coverage | Notes |
|---------|--------------|-------|
| User Authentication | Partial | Basic login/logout tested |
| Game Type Listing | Complete | |
| Game Instance Creation | Complete | |
| Game Instance Joining | Partial | Edge cases needed |
| Waiting Room | Minimal | |
| WebSocket Communication | Minimal | Only validation tested |

## Planned Features

- Game history and statistics
- User profiles and preferences
- Additional game types
- Chat functionality in waiting rooms
- Spectator mode for ongoing games
