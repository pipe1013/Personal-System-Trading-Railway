# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Environment-specific database path
if os.getenv('RAILWAY_ENVIRONMENT'):
    # For Railway deployment - use tmp directory for persistence
    DB_PATH = os.getenv('DB_PATH', '/tmp/trading_system.db')
else:
    # For local development
    DB_PATH = os.path.join(BASE_DIR, 'trading_system.db')