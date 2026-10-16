import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

from app import create_app
from app.migrations_helper import upgrade_existing_sqlite_database

config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

# Ensure legacy SQLite database (if present) is upgraded seamlessly
db_path = os.path.join(os.path.dirname(__file__), 'localshare.db')
upgrade_existing_sqlite_database(db_path)

if __name__ == '__main__':
    # For local execution: default to debug=True only if FLASK_DEBUG is enabled or in development
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() in ('true', '1')
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=debug_mode)
