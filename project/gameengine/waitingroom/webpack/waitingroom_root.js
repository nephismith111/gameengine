// Import jQuery
import $ from 'jquery';
import WebSocketClient from '../../gameengine/webpack/websocket_client';

// API URLs
const API_URLS = {
    GAME_INSTANCE: (gameId) => `/gameengine/v1/game-instances/${gameId}/`,
    START_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/start/`,
    UPDATE_SETTINGS: (gameId) => `/gameengine/v1/game-instances/${gameId}/settings/`,
    LEAVE_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/leave/`
};

// WebSocket client
let wsClient = null;

// Initialize the waiting room
$(document).ready(function() {
    const gameId = $('#game-id').val();
    
    if (!gameId) {
        showError('Game ID not found');
        return;
    }
    
    // Load game data
    loadGameData(gameId);
    
    // Set up event handlers
    $('#start-game-btn').on('click', function() {
        startGame(gameId);
    });
    
    $('#save-settings-btn').on('click', function() {
        saveGameSettings(gameId);
    });
    
    // Add leave game button handler
    $('#leave-game-btn').on('click', function() {
        leaveGame(gameId);
    });
    
    // Set up settings validation on blur
    $('#settings-editor').on('blur', function() {
        validateSettingsJSON();
    });
    
    // Set up WebSocket connection
    setupWebSocket(gameId);
    
    // Set up polling to refresh game data (as a fallback)
    setInterval(function() {
        loadGameData(gameId);
    }, 10000); // Refresh every 10 seconds
});

/**
 * Set up WebSocket connection for real-time updates
 */
function setupWebSocket(gameId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/waitingroom/${gameId}/`;
    
    wsClient = new WebSocketClient(wsUrl);
    
    // Register message handlers
    wsClient.on('settings_update', handleSettingsUpdate);
    wsClient.on('waitingroom_update', handleWaitingRoomUpdate);
    
    // Connect to the WebSocket server
    wsClient.connect();
}

/**
 * Handle settings update messages from WebSocket
 */
function handleSettingsUpdate(data) {
    console.log('Settings update received:', data);
    
    // Update the settings display
    updateGameSettings(data.game_settings);
    
    // Show a notification
    const updatedBy = data.updated_by.username;
    showInfo(`Game settings updated by ${updatedBy}`);
}

/**
 * Handle waiting room update messages from WebSocket
 */
function handleWaitingRoomUpdate(data) {
    console.log('Waiting room update received:', data);
    
    // Update the entire waiting room UI with the new data
    updateWaitingRoom(data.game_data);
    
    // Show a notification
    showInfo('Waiting room updated');
}

/**
 * Load game data from the API
 */
function loadGameData(gameId) {
    $.ajax({
        url: API_URLS.GAME_INSTANCE(gameId),
        type: 'GET',
        success: function(response) {
            updateWaitingRoom(response);
        },
        error: function(xhr, status, error) {
            console.error('Failed to load game data:', error);
            showError('Failed to load game data. Please try refreshing the page.');
        }
    });
}

/**
 * Update the waiting room UI with game data
 */
function updateWaitingRoom(gameData) {
    // Update game info
    $('#game-name').text(gameData.instance_name);
    $('#game-type').text(gameData.game_type.name);
    $('#game-description').text(gameData.game_type.description);
    
    // Update players list
    updatePlayersList(gameData.joined_users);
    
    // Update game settings
    updateGameSettings(gameData.game_settings);
    
    // Show/hide creator controls
    updateCreatorControls(gameData);
    
    // Check if game has started
    if (gameData.status === 'ongoing') {
        // Redirect to the game page
        window.location.href = `/games/${gameData.game_type.name.toLowerCase()}/${gameData.id}/`;
    }
}

/**
 * Update the list of players in the waiting room
 */
function updatePlayersList(players) {
    if (!players || players.length === 0) {
        $('#players-list').html('<li class="list-group-item">No players have joined yet.</li>');
        return;
    }
    
    let html = '';
    players.forEach(function(player) {
        const creatorBadge = player.is_creator ? 
            '<span class="badge bg-primary ms-2">Creator</span>' : '';
        
        html += `<li class="list-group-item">${player.username}${creatorBadge}</li>`;
    });
    
    $('#players-list').html(html);
}

/**
 * Update the creator controls based on the current user's role
 */
function updateCreatorControls(gameData) {
    // Check if current user is the creator
    const currentUserId = getCurrentUserId();
    const isCreator = gameData.joined_users.some(user => 
        user.id === currentUserId && user.is_creator
    );
    
    if (isCreator && gameData.status === 'pending') {
        $('#creator-controls').show();
        $('#settings-editor').prop('disabled', false);
        $('#save-settings-btn').prop('disabled', false);
    } else {
        $('#creator-controls').hide();
        $('#settings-editor').prop('disabled', true);
        $('#save-settings-btn').prop('disabled', true);
    }
}

/**
 * Update the game settings display
 */
function updateGameSettings(gameSettings) {
    if (!gameSettings) {
        return;
    }
    
    // Format the JSON with indentation for better readability
    const formattedSettings = JSON.stringify(gameSettings, null, 2);
    
    // Update the textarea if it doesn't have focus (to avoid disrupting user editing)
    if (!$('#settings-editor').is(':focus')) {
        $('#settings-editor').val(formattedSettings);
    }
}

/**
 * Start the game
 */
function startGame(gameId) {
    $.ajax({
        url: API_URLS.START_GAME(gameId),
        type: 'POST',
        success: function(response) {
            // Game started successfully, will be redirected on next data refresh
        },
        error: function(xhr, status, error) {
            console.error('Failed to start game:', error);
            showError('Failed to start the game. Please try again.');
        }
    });
}

/**
 * Leave the waiting room
 */
function leaveGame(gameId) {
    if (confirm('Are you sure you want to leave this game?')) {
        $.ajax({
            url: API_URLS.LEAVE_GAME(gameId),
            type: 'POST',
            success: function(response) {
                // Redirect to the home page
                window.location.href = '/';
            },
            error: function(xhr, status, error) {
                console.error('Failed to leave game:', error);
                showError('Failed to leave the game. Please try again.');
            }
        });
    }
}

/**
 * Show an error message
 */
function showError(message) {
    showNotification(message, 'danger');
}

/**
 * Get the current user's ID
 * This is a placeholder - you'll need to implement this based on your authentication system
 */
function getCurrentUserId() {
    // This should be replaced with actual code to get the current user's ID
    // For now, we'll just return a placeholder
    return parseInt($('meta[name="user-id"]').attr('content') || '0');
}

/**
 * Validate the settings JSON in the editor
 * Returns true if valid, false if invalid
 */
function validateSettingsJSON() {
    const settingsText = $('#settings-editor').val();
    try {
        JSON.parse(settingsText);
        // If we get here, JSON is valid
        $('#settings-editor').removeClass('is-invalid').addClass('is-valid');
        $('#settings-validation-feedback').hide();
        return true;
    } catch (e) {
        // Invalid JSON
        $('#settings-editor').removeClass('is-valid').addClass('is-invalid');
        $('#settings-validation-feedback').text('Invalid JSON: ' + e.message).show();
        return false;
    }
}

/**
 * Save the game settings
 */
function saveGameSettings(gameId) {
    // First validate the JSON
    if (!validateSettingsJSON()) {
        return;
    }
    
    const settingsText = $('#settings-editor').val();
    const settings = JSON.parse(settingsText);
    
    $.ajax({
        url: API_URLS.UPDATE_SETTINGS(gameId),
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ game_settings: settings }),
        success: function(response) {
            showSuccess('Game settings updated successfully');
        },
        error: function(xhr, status, error) {
            console.error('Failed to update game settings:', error);
            showError('Failed to update game settings. Please try again.');
        }
    });
}

/**
 * Show a success message in the notification area
 */
function showSuccess(message) {
    showNotification(message, 'success');
}

/**
 * Show an info message in the notification area
 */
function showInfo(message) {
    showNotification(message, 'info');
}

/**
 * Show a notification in the dedicated notification area
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
    
    // Add to notification area
    $('#notification-area').append(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        notification.alert('close');
    }, 5000);
}
