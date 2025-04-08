/**
 * Functions for handling game instances
 */
import $ from 'jquery';
import API_URLS from './api_urls';

/**
 * Load game instances from the API
 */
function loadGameInstances() {
    $.ajax({
        url: API_URLS.GAME_INSTANCES,
        type: 'GET',
        success: function(response) {
            renderGameInstances(response.game_instances);
        },
        error: function(xhr, status, error) {
            console.error('Failed to load game instances:', error);
            $('#game-instances-table tbody').html(
                '<tr><td colspan="6" class="text-center">Failed to load game instances. Please try refreshing the page.</td></tr>'
            );
        }
    });
}

/**
 * Render game instances in the UI
 * @param {Array} gameInstances - The game instances to render
 */
function renderGameInstances(gameInstances) {
    if (!gameInstances || gameInstances.length === 0) {
        $('#game-instances-table tbody').html(
            '<tr><td colspan="6" class="text-center">No game instances available.</td></tr>'
        );
        return;
    }

    let html = '';
    gameInstances.forEach(function(instance) {
        const statusClass = getStatusClass(instance.status);
        const playerNames = instance.joined_users.map(user => user.username).join(', ');
        
        html += `
            <tr class="${statusClass}">
                <td>${instance.game_type.name}</td>
                <td>${instance.instance_name}</td>
                <td>${capitalizeFirstLetter(instance.status)}</td>
                <td>${instance.player_count}/${instance.game_type.max_players}</td>
                <td>${playerNames}</td>
                <td>
                    ${getActionButton(instance)}
                </td>
            </tr>
        `;
    });

    $('#game-instances-table tbody').html(html);
}

/**
 * Get the CSS class for a game status
 * @param {string} status - The game status
 * @returns {string} The CSS class
 */
function getStatusClass(status) {
    switch (status) {
        case 'pending':
            return 'table-info';
        case 'ongoing':
            return 'table-success';
        case 'ended':
            return 'table-secondary';
        default:
            return '';
    }
}

/**
 * Get the action button HTML for a game instance
 * @param {object} instance - The game instance
 * @returns {string} The HTML for the action button
 */
function getActionButton(instance) {
    if (instance.status === 'pending' && instance.is_joinable) {
        return `<button class="btn btn-sm btn-success join-game-btn" data-game-id="${instance.id}">Join</button>`;
    } else if (instance.status === 'ongoing') {
        return `<a href="/waitingroom/${instance.id}/" class="btn btn-sm btn-primary">View</a>`;
    } else if (instance.status === 'ended') {
        return `<button class="btn btn-sm btn-secondary" disabled>Ended</button>`;
    } else {
        return `<button class="btn btn-sm btn-secondary" disabled>Full</button>`;
    }
}

/**
 * Join a game instance
 * @param {string} gameId - The ID of the game to join
 */
function joinGame(gameId) {
    $.ajax({
        url: API_URLS.JOIN_GAME(gameId),
        type: 'POST',
        success: function(response) {
            // Navigate to the waiting room
            window.location.href = `/waitingroom/${gameId}/`;
        },
        error: function(xhr, status, error) {
            console.error('Failed to join game:', error);
            alert('Failed to join game. Please try again.');
        }
    });
}

/**
 * Capitalize the first letter of a string
 * @param {string} string - The string to capitalize
 * @returns {string} The capitalized string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export { loadGameInstances, joinGame, capitalizeFirstLetter };
