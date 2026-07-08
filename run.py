#!/usr/bin/env python3
"""
Spouštěcí skript aplikace.
Použití: python run.py
"""

from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    print("=" * 60)
    print("Generátor průvodek a štítků")
    print("=" * 60)
    print("\nServer spoušten na: http://0.0.0.0:5000")
    print("Pro přístup otevřete v prohlížeči: http://localhost:5000")
    print("\nVýchozí přihlašovací údaje:")
    print("  Uživatel: admin")
    print("  Heslo:    admin123")
    print("\nDŮLEŽITÉ: Změňte výchozí heslo po prvním přihlášení!")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
