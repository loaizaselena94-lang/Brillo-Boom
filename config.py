import os

class Config:
    SECRET_KEY                  = os.environ.get('SECRET_KEY') or 'brillo-boom-secret-2025'
    SQLALCHEMY_DATABASE_URI     = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/brillo_boom'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE       = False
    SESSION_COOKIE_HTTPONLY     = True
    PERMANENT_SESSION_LIFETIME  = 3600          # 1 hora

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
