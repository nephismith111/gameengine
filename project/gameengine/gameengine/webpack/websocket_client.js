/**
 * WebSocket client for handling real-time communication
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
     * @private
     */
    _onOpen(event) {
        console.log('WebSocket connection established');
        this.connected = true;
    }

    /**
     * Handle WebSocket close event
     * @private
     */
    _onClose(event) {
        console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
        this.connected = false;
        this.socket = null;
    }

    /**
     * Handle WebSocket message event
     * @private
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
     * @private
     */
    _onError(error) {
        console.error('WebSocket error:', error);
    }
}

export default WebSocketClient;
