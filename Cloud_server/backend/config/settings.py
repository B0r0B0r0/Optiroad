import os

class Config:
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # URLs
    NGINX_URL = os.environ.get('NGINX_URL')
    
    # Security
    SECRET_KEY = 'super_secret_key'  # TODO: Move to environment variable
    TEMP = False  # Change when moving to HTTPS
    
    # JWT Configuration
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = 'access_token'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token'
    JWT_ACCESS_TOKEN_EXPIRES = 900  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Session Configuration
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    
    # Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = "stinaalin@gmail.com"
    MAIL_PASSWORD = "skgr kvav qjtc vdbp"
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # Token Expiration Times
    ACCESS_EXP_TIME = 900
    REFRESH_EXP_TIME = 2592000

    MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "id-cards")

    MONGO_URI = "mongodb://admin:secret123@mongo_container:27017"
    DB_NAME = "ppo_results"