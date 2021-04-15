import os

class Config(object):
    """Base Config Object"""
    DEBUG = False
    #SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = 'secretkey'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://dailyd:ch3Mi$try@localhost/daily_delight')
    SQLALCHEMY_DATABASE_URI = 'postgresql://dailyd:ch3Mi$try@localhost/daily_delight'
    CORS_HEADERS = 'Content-Type'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # This is just here to suppress a warning from SQLAlchemy as it will soon be removed

class DevelopmentConfig(Config):
    """Development Config that extends the Base Config Object"""
    DEVELOPMENT = True
    DEBUG = True

class ProductionConfig(Config):
    """Production Config that extends the Base Config Object"""
    DEBUG = True