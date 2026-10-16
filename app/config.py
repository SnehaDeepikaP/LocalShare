import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-localshare-insecure-key-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Matching algorithm parameters
    MATCHING_MIN_SCORE = 30
    ITEMS_PER_PAGE = 6
    
    # Security Rate Limiting
    LOGIN_RATE_LIMIT_ATTEMPTS = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes


_default_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'localshare.db')).replace('\\', '/')
_default_db_uri = f"sqlite:///{_default_db_path}"

class DevelopmentConfig(Config):
    DEBUG = True
    _db_env = os.environ.get('DATABASE_URL')
    if _db_env and _db_env.startswith('sqlite:///') and not (len(_db_env) > 11 and _db_env[11] == ':'):
        # Resolve relative SQLite URL to application root
        _rel_path = _db_env[10:]
        _abs_p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', _rel_path)).replace('\\', '/')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_abs_p}"
    else:
        SQLALCHEMY_DATABASE_URI = _db_env or _default_db_uri
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'test-secret-key-for-localshare-tests'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # In production, require SECRET_KEY from environment
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True  # Enforce HTTPS cookies in production


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
