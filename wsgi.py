import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.migrations_helper import upgrade_existing_sqlite_database

config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

# Ensure database tables exist on startup
db_path = os.path.join(os.path.dirname(__file__), 'localshare.db')
upgrade_existing_sqlite_database(db_path)

if __name__ == "__main__":
    app.run()
