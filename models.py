from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Uživatelé aplikace."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operátor')  # admin, mistr, operátor, viewer
    full_name = db.Column(db.String(120), nullable=True)  # Jméno a příjmení pro průvodky
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relace: dokumenty vytvořené uživatelem
    documents = db.relationship('Document', backref='creator', lazy=True)
    templates = db.relationship('Template', backref='owner', lazy=True)

    def set_password(self, password):
        """Nastavení hesla (hash)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Ověření hesla."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_master(self):
        return self.role in ['admin', 'mistr']

    def can_operate(self):
        return self.role in ['admin', 'mistr', 'operátor']

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Template(db.Model):
    """Šablony pro generování průvodek a štítků."""

    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(20), nullable=False)  # pruvodka_stroje, pruvodka_svarovna, stitek
    content_json = db.Column(db.Text, nullable=True)  # JSON s parametry šablony
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Template {self.name} ({self.template_type})>'


class Document(db.Model):
    """Archivované dokumenty (PDF)."""

    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(20), nullable=False)  # pruvodka_stroje, pruvodka_svarovna, stitek
    title = db.Column(db.String(200), nullable=False)
    production_number = db.Column(db.String(100), nullable=True)  # Výrobní číslo/kooperace
    machine = db.Column(db.String(100), nullable=True)  # Stroj
    category = db.Column(db.String(100), nullable=True)  # Kategorie (pro svařovnu)
    operation = db.Column(db.String(100), nullable=True)  # Operace
    pdf_data = db.Column(db.LargeBinary, nullable=True)  # PDF uložené v DB (BLOB)
    file_path = db.Column(db.String(500), nullable=True)  # Nebo cesta k souboru
    extra_data = db.Column(db.Text, nullable=True)  # Další údaje jako JSON
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.title} ({self.document_type})>'
