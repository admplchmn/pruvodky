from functools import wraps
from flask import flash, redirect, url_for, render_template
from flask_login import current_user

def login_required(f):
    """Decorator - vyžaduje přihlášení."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Pro přístup k této stránce je nutné se přihlásit.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator - vyžaduje roli admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('K tomuto obsahu nemáte přístupová práva.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def master_required(f):
    """Decorator - vyžaduje roli admin nebo mistr."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_master():
            flash('K tomuto obsahu nemáte přístupová práva.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def can_operate_required(f):
    """Decorator - vyžaduje roli admin, mistr nebo operátor."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_operate():
            flash('K tomuto obsahu nemáte přístupová práva.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
