// Import jQuery
import $ from 'jquery';

// Import custom CSS
import './game_tiles.css';

// Import modules
import WebSocketClient from './websocket_client';
import API_URLS from './api_urls';
import { loadGameTypes, showNewGameModal, createNewGame } from './game_types';
import { loadGameInstances, joinGame } from './game_instances';
import { triggerWebSocketMessage } from './utils';

/**
 * Set up event handlers for the page
 */
function setupEventHandlers() {
    // Event delegation for game type cards
    $(document).on('click', '.game-type-card', function(e) {
        e.preventDefault();
        const gameTypeId = $(this).data('game-type-id');
        showNewGameModal(gameTypeId);
    });
    
    // Event delegation for join game buttons
    $(document).on('click', '.join-game-btn', function(e) {
        e.preventDefault();
        const gameId = $(this).data('game-id');
        joinGame(gameId);
    });
    
    // Create game button in modal
    $('#createGameBtn').on('click', function() {
        createNewGame();
    });
    
    // Handle Enter key in the instance name input
    $('#instanceName').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            createNewGame();
        }
    });
    
    // Refresh game instances periodically
    setInterval(loadGameInstances, 10000); // Refresh every 10 seconds
}

/**
 * Initialize the game container
 */
function initGameContainer() {
    console.log('Game container initialized');
    loadGameTypes();
    loadGameInstances();
    setupEventHandlers();
}

// Initialize when the document is ready
$(document).ready(function() {
    console.log('Document ready, initializing game container');
    initGameContainer();
    
    // Create and connect the WebSocket client
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/validate/`;
    const wsClient = new WebSocketClient(wsUrl);
    
    // Connect to the WebSocket server
    wsClient.connect();
    
    // Register message handlers
    wsClient.on('validation_message', function(data) {
        console.log('Validation message received:', data.message);
        $('#game-container').append(
            `<div class="alert alert-info mt-3">${data.message}</div>`
        );
    });
    
    // Add click handler to the heading
    $('h1').css('cursor', 'pointer').click(function() {
        console.log('Heading clicked, triggering WebSocket message');
        triggerWebSocketMessage();
    });
});
