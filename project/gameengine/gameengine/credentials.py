"""
Credentials and connection details for external services.
This file should not be committed to version control in a real project.
"""
from typing import Final

# Database credentials
DB_HOST: Final[str] = 'db'
DB_PORT: Final[str] = '5432'
DB_NAME: Final[str] = 'gameengine'
DB_USER: Final[str] = 'postgres'
DB_PASSWORD: Final[str] = 'postgres'

# Redis connection
REDIS_HOST: Final[str] = 'redis'
REDIS_PORT: Final[str] = '6379'
