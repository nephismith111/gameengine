"""
Environment metadata such as hostnames and deployment context
"""

import os

# Determine environment
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# Base URLs
API_BASE_URL = '/api/v1'
WEBSOCKET_BASE_URL = 'ws://'

# Deployment info
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_STAGING = ENVIRONMENT == 'staging'
IS_DEVELOPMENT = ENVIRONMENT == 'development'
