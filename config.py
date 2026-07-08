import os
from datetime import timedelta

class Config:
    """Základní konfigurace aplikace."""

    # Cesta k databázi (SQLite)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "pruvodky.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key pro session a tokeny
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Časové nastavení session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Cesta pro uploady (pokud budeme ukládat PDF na disk)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
