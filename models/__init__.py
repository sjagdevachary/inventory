"""
Database models package.
Exports the shared SQLAlchemy instance and all models.
"""
from flask_sqlalchemy import SQLAlchemy

# Shared database instance — imported by app.py and all models
db = SQLAlchemy()

from models.user import User
from models.product import Product
from models.sale import Sale
