/**
 * API URL definitions for the Game Engine application
 */
const API_URLS = {
    GAME_TYPES: '/gameengine/v1/game-types/',
    GAME_INSTANCES: '/gameengine/v1/game-instances/',
    JOIN_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/join/`,
    START_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/start/`,
    TRIGGER_WEBSOCKET: '/gameengine/v1/trigger-websocket/'
};

export default API_URLS;
