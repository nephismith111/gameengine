/**
 * Functions for handling game types
 */
import $ from 'jquery';
import API_URLS from './api_urls';

/**
 * Load game types from the API
 */
function loadGameTypes() {
    $.ajax({
        url: API_URLS.GAME_TYPES,
        type: 'GET',
        success: function(response) {
            renderGameTypes(response.game_types);
        },
        error: function(xhr, status, error) {
            console.error('Failed to load game types:', error);
            $('#game-types-container').html(
                '<div class="col-12"><div class="alert alert-danger">Failed to load game types. Please try refreshing the page.</div></div>'
            );
        }
    });
}

/**
 * Render game types in the UI
 * @param {Array} gameTypes - The game types to render
 */
function renderGameTypes(gameTypes) {
    if (!gameTypes || gameTypes.length === 0) {
        $('#game-types-container').html(
            '<div class="col-12"><div class="alert alert-warning">No game types available.</div></div>'
        );
        return;
    }

    let html = '<h2 class="section-title">Available Games <small>(Click a game to create a new instance)</small></h2>';
    html += '<div class="row row-cols-1 row-cols-md-3 g-4">';
    
    gameTypes.forEach(function(gameType) {
        html += `
            <div class="col">
                <div class="card game-type-card" data-game-type-id="${gameType.id}">
                    <img src="${gameType.image_url}" class="card-img-top" alt="${gameType.name}">
                    <div class="card-body">
                        <h5 class="card-title">${gameType.name}</h5>
                        <p class="card-text">${gameType.description}</p>
                    </div>
                    <div class="card-footer">
                        Max Players: ${gameType.max_players}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    $('#game-types-container').html(html);
}

/**
 * Show the new game modal for a specific game type
 * @param {number} gameTypeId - The ID of the selected game type
 */
function showNewGameModal(gameTypeId) {
    // Store the selected game type ID
    $('#gameTypeId').val(gameTypeId);
    $('#instanceName').val('');
    
    // Get the game type name for better UX
    const gameTypeName = $('.game-type-card[data-game-type-id="' + gameTypeId + '"] .card-title').text();
    $('#selectedGameType').text(gameTypeName);
    
    // Show the modal using Bootstrap 5 Modal API
    const modalElement = document.getElementById('newGameModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Focus on the instance name input after modal is shown
    modalElement.addEventListener('shown.bs.modal', function () {
        $('#instanceName').focus();
    });
}

/**
 * Create a new game instance
 */
function createNewGame() {
    const gameTypeId = $('#gameTypeId').val();
    const instanceName = $('#instanceName').val().trim();
    
    if (!instanceName) {
        alert('Please enter a game name');
        return;
    }
    
    $.ajax({
        url: API_URLS.GAME_INSTANCES,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            game_type_id: parseInt(gameTypeId),
            instance_name: instanceName
        }),
        success: function(response) {
            // Hide the modal using Bootstrap 5 Modal API
            const modalElement = document.getElementById('newGameModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
            
            // Navigate to the waiting room
            window.location.href = `/waitingroom/${response.id}/`;
        },
        error: function(xhr, status, error) {
            console.error('Failed to create game:', error);
            alert('Failed to create game. Please try again.');
        }
    });
}

export { loadGameTypes, showNewGameModal, createNewGame };
