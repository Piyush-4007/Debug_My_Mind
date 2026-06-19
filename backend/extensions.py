"""Shared extension instances, initialised in the app factory.

Kept in their own module to avoid circular imports between app.py and models.
"""
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
