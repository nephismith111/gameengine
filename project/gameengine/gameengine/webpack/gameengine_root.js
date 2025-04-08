// Import jQuery
import $ from 'jquery';

// API URLs
const API_URLS = {
    GAME_TYPES: '/gameengine/v1/game-types/',
    GAME_INSTANCES: '/gameengine/v1/game-instances/',
    JOIN_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/join/`,
    START_GAME: (gameId) => `/gameengine/v1/game-instances/${gameId}/start/`
};

/**
 * WebSocket client class to handle WebSocket connections
 */
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.connected = false;
        this.messageHandlers = {};
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.socket) {
            console.log('WebSocket already connected');
            return;
        }

        console.log(`Connecting to WebSocket at ${this.url}`);
        this.socket = new WebSocket(this.url);

        this.socket.onopen = this._onOpen.bind(this);
        this.socket.onclose = this._onClose.bind(this);
        this.socket.onmessage = this._onMessage.bind(this);
        this.socket.onerror = this._onError.bind(this);
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.socket) {
            console.log('Closing WebSocket connection');
            this.socket.close();
            this.socket = null;
            this.connected = false;
        }
    }

    /**
     * Send a message to the WebSocket server
     */
    sendMessage(message) {
        if (!this.connected) {
            console.error('Cannot send message: WebSocket not connected');
            return;
        }

        const messageString = typeof message === 'string' 
            ? message 
            : JSON.stringify(message);
        
        this.socket.send(messageString);
    }

    /**
     * Register a handler for a specific message type
     */
    on(messageType, handler) {
        if (!this.messageHandlers[messageType]) {
            this.messageHandlers[messageType] = [];
        }
        this.messageHandlers[messageType].push(handler);
    }

    /**
     * Handle WebSocket open event
     */
    _onOpen(event) {
        console.log('WebSocket connection established');
        this.connected = true;
    }

    /**
     * Handle WebSocket close event
     */
    _onClose(event) {
        console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
        this.connected = false;
        this.socket = null;
    }

    /**
     * Handle WebSocket message event
     */
    _onMessage(event) {
        console.log('WebSocket message received:', event.data);
        
        try {
            const data = JSON.parse(event.data);
            const messageType = data.type || 'unknown';
            
            // Call all handlers for this message type
            if (this.messageHandlers[messageType]) {
                this.messageHandlers[messageType].forEach(handler => {
                    handler(data);
                });
            }
            
            // Call all handlers for 'all' message type
            if (this.messageHandlers['all']) {
                this.messageHandlers['all'].forEach(handler => {
                    handler(data);
                });
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket error event
     */
    _onError(error) {
        console.error('WebSocket error:', error);
    }
}

// Function to initialize the game container
function initGameContainer() {
    console.log('Game container initialized');
    loadGameTypes();
    loadGameInstances();
    setupEventHandlers();
}

/**
 * Load and display all available game types
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
 * Render game types as tiles
 */
function renderGameTypes(gameTypes) {
    if (!gameTypes || gameTypes.length === 0) {
        $('#game-types-container').html(
            '<div class="col-12"><div class="alert alert-warning">No game types available.</div></div>'
        );
        return;
    }

    let html = '';
    gameTypes.forEach(function(gameType) {
        html += `
            <div class="col-md-4 mb-4">
                <div class="card game-type-card" data-game-type-id="${gameType.id}">
                    <img src="${gameType.image_url}" class="card-img-top" alt="${gameType.name}" style="height: 180px; object-fit: contain; padding: 15px;">
                    <div class="card-body">
                        <h5 class="card-title">${gameType.name}</h5>
                        <p class="card-text">${gameType.description}</p>
                        <p class="card-text"><small class="text-muted">Max Players: ${gameType.max_players}</small></p>
                        <button class="btn btn-primary create-game-btn">Create Game</button>
                    </div>
                </div>
            </div>
        `;
    });

    $('#game-types-container').html(html);
}

/**
 * Load and display all game instances
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
 * Render game instances in the table
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
 * Get the appropriate CSS class for a game status
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
 * Get the appropriate action button for a game instance
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
 * Capitalize the first letter of a string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Set up event handlers for the page
 */
function setupEventHandlers() {
    // Event delegation for game type cards
    $(document).on('click', '.create-game-btn', function(e) {
        e.preventDefault();
        const gameTypeId = $(this).closest('.game-type-card').data('game-type-id');
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
    
    // Refresh game instances periodically
    setInterval(loadGameInstances, 10000); // Refresh every 10 seconds
}

/**
 * Show the modal for creating a new game
 */
function showNewGameModal(gameTypeId) {
    $('#gameTypeId').val(gameTypeId);
    $('#instanceName').val('');
    $('#newGameModal').modal('show');
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
            $('#newGameModal').modal('hide');
            // Navigate to the waiting room
            window.location.href = `/waitingroom/${response.id}/`;
        },
        error: function(xhr, status, error) {
            console.error('Failed to create game:', error);
            alert('Failed to create game. Please try again.');
        }
    });
}

/**
 * Join an existing game
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

// Function to trigger the WebSocket message via API
function triggerWebSocketMessage() {
    $.ajax({
        url: '/gameengine/v1/trigger-websocket/',
        type: 'POST',
        contentType: 'application/json',
        success: function(response) {
            console.log('API call successful:', response);
        },
        error: function(xhr, status, error) {
            console.error('API call failed:', error);
            console.error('Response:', xhr.responseText);
        }
    });
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
