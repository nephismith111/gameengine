/**
 * Utility functions for the Game Engine application
 */
import $ from 'jquery';
import API_URLS from './api_urls';

/**
 * Trigger a WebSocket message via the API
 */
function triggerWebSocketMessage() {
    $.ajax({
        url: API_URLS.TRIGGER_WEBSOCKET,
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

export { triggerWebSocketMessage };
