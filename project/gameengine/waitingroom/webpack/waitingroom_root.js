// Import jQuery
import $ from 'jquery';

// API URLs
const API_URLS = {
    GAME_INSTANCE: (gameId) => `/gameengine/v1/game-instances/${gameId}/`,
    START_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/start/`
};

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
    
    // Set up polling to refresh game data
    setInterval(function() {
        loadGameData(gameId);
    }, 5000); // Refresh every 5 seconds
});

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
    } else {
        $('#creator-controls').hide();
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
 * Show an error message
 */
function showError(message) {
    $('.card-body').prepend(
        `<div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`
    );
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
