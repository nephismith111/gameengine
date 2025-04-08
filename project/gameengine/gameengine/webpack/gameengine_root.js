// Import jQuery
import $ from 'jquery';

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
    $('#game-container').html('<div class="alert alert-success">Hello World from Webpack!</div>');
    console.log('Game container initialized');
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
