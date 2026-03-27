"""
Configuration settings for the Smart Inventory Management System.
"""
import os
from dotenv import load_dotenv
load_dotenv()


# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration — SQLite stored in /database folder
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)

default_db = f"sqlite:///{os.path.join(DATABASE_DIR, 'inventory.db')}"
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default_db)
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://")

SQLALCHEMY_TRACK_MODIFICATIONS = False


# Secret key for session management (change in production!)
SECRET_KEY = os.getenv('SECRET_KEY', 'smart-inventory-secret-key-2024')

# Inventory settings
LOW_STOCK_THRESHOLD = 10  # Alert when quantity falls below this
