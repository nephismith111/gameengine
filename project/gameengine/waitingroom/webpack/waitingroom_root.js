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
    
    // Create notification area if it doesn't exist
    if ($('#notification-area').length === 0) {
        // Try to add it after players card
        if ($('#players-card').length > 0) {
            $('#players-card').after('<div id="notification-area" class="mt-3"></div>');
        } 
        // If players card doesn't exist yet, add it to the main container
        else {
            $('.container').append('<div id="notification-area" class="mt-3"></div>');
        }
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
    
    // Show a welcome notification
    setTimeout(function() {
        showInfo('Welcome to the waiting room');
    }, 1000);
});

/**
 * Set up WebSocket connection for real-time updates
 */
function setupWebSocket(gameId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/waitingroom/${gameId}/`;
    
    console.log('Setting up WebSocket connection to:', wsUrl);
    
    wsClient = new WebSocketClient(wsUrl);
    
    // Register message handlers
    wsClient.on('settings_update', handleSettingsUpdate);
    wsClient.on('waitingroom_update', handleWaitingRoomUpdate);
    wsClient.on('connection_established', function(data) {
        console.log('WebSocket connection established:', data);
        showSuccess('Connected to waiting room');
    });
    
    // Connect to the WebSocket server
    wsClient.connect();
    
    // Add reconnection logic
    window.addEventListener('online', function() {
        if (wsClient && !wsClient.connected) {
            console.log('Network connection restored, reconnecting WebSocket...');
            wsClient.connect();
        }
    });
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
    
    // Don't show notification to the user who made the change
    const currentUserId = getCurrentUserId();
    if (currentUserId !== data.updated_by.id) {
        showInfo(`Game settings updated by ${updatedBy}`);
    }
    
    // TODO: Fix notification not showing up on remote browsers
    // The update is coming through on remote browsers but the notification isn't displaying
    // Possible issues:
    // 1. Bootstrap Toast initialization failing
    // 2. CSS/styling issues preventing visibility
    // 3. Timing issues with DOM elements
    // 4. User ID comparison logic incorrect
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
    
    // Update game image
    if (gameData.game_type.image_url) {
        if ($('#game-image').length === 0) {
            // Add image container if it doesn't exist
            $('#game-info').append('<div class="text-center mt-3"><img id="game-image" class="img-fluid rounded" style="max-height: 200px;" alt="Game image"></div>');
        }
        $('#game-image').attr('src', gameData.game_type.image_url);
    }
    
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
    
    // Ensure notification area exists after updating players list
    // This is a good place to ensure it exists since we know the players card exists at this point
    ensureNotificationArea();
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
    
    console.log('Updating game settings display with:', gameSettings);
    
    // Format the JSON with indentation for better readability
    const formattedSettings = JSON.stringify(gameSettings, null, 2);
    
    // Update the textarea if it doesn't have focus (to avoid disrupting user editing)
    if (!$('#settings-editor').is(':focus')) {
        $('#settings-editor').val(formattedSettings);
        
        // Add a visual indicator that settings were updated
        $('#settings-card').addClass('border-success');
        $('#settings-card .card-header').addClass('bg-success text-white');
        
        // Flash effect to draw attention
        setTimeout(function() {
            $('#settings-card').removeClass('border-success');
            $('#settings-card .card-header').removeClass('bg-success text-white');
        }, 2000);
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
 * Show a notification as a Bootstrap toast
 */
function showNotification(message, type = 'info') {
    console.log('Showing notification:', message, type);
    
    // Ensure toast container exists
    ensureNotificationArea();
    
    // Map type to Bootstrap background class
    const bgClass = type === 'info' ? 'bg-info' : 
                   type === 'success' ? 'bg-success' : 
                   type === 'warning' ? 'bg-warning' : 
                   type === 'danger' ? 'bg-danger' : 'bg-secondary';
    
    // Create a unique ID for this toast
    const toastId = 'toast-' + Date.now();
    
    // Create toast element
    const toast = $(`
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">Game Engine</strong>
                <small>${new Date().toLocaleTimeString()}</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `);
    
    // Add to toast container
    $('#toast-container').append(toast);
    
    // Initialize and show the toast
    try {
        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement);
        bsToast.show();
    } catch (e) {
        console.error('Error showing toast:', e);
        // Fallback if Bootstrap Toast API fails
        toast.fadeIn();
        setTimeout(() => toast.fadeOut(400, function() { $(this).remove(); }), 5000);
    }
}

/**
 * Ensure the notification area exists and is visible
 */
function ensureNotificationArea() {
    if ($('#toast-container').length === 0) {
        // Create a toast container at the bottom right of the screen
        $('body').append(`
            <div id="toast-container" class="position-fixed bottom-0 end-0 p-3" 
                 style="z-index: 1050;"></div>
        `);
        console.log('Created toast container');
    }
}
