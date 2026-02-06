# config.py
import os
from urllib.parse import quote_plus

class Config:
    # Get database configuration from environment variables
    DB_HOST = os.getenv('DB_HOST', '192.168.1.186')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'marisa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'marisa@123')
    DB_NAME = os.getenv('DB_NAME', 'misc')
    
    # URL encode the password to handle special characters
    encoded_password = quote_plus(DB_PASSWORD)
    
    # MySQL database configuration using the pymysql driver
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'asghjas567as')  # Change this to a secure key in production
    JWT_TOKEN_LOCATION = ['headers']    # Where to look for the JWT (headers, cookies, etc.)
    # Optionally, you can also configure:
    # JWT_ACCESS_TOKEN_EXPIRES = 3600  # Token expiration time in seconds