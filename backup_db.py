#!/usr/bin/env python3
"""
Skript pro zálohu a obnovu databáze.

Použití:
    python backup_db.py backup          # Vytvořit zálohu
    python backup_db.py restore         # Obnovit z poslední zálohy
    python backup_db.py list            # Seznam všech záloh
    python backup_db.py cleanup 7       # Smazat starší než X dní (default 7)
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "pruvodky.db"
BACKUP_DIR = BASE_DIR / "backups"


def ensure_backup_dir():
    """Vytvoří adresář pro zálohy pokud neexistuje."""
    BACKUP_DIR.mkdir(exist_ok=True)


def get_backup_filename():
    """Generuje název souboru pro zálohu."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"pruvodky_backup_{timestamp}.db"


def backup_database():
    """Vytvoří zálohu databáze."""
    if not DB_PATH.exists():
        print("✗ Databáze neexistuje!")
        return False

    ensure_backup_dir()

    backup_path = BACKUP_DIR / get_backup_filename()

    try:
        shutil.copy2(DB_PATH, backup_path)
        file_size = backup_path.stat().st_size
        print(f"✓ Záloha vytvořena: {backup_path}")
        print(f"  Velikost: {file_size:,} bajtů")
        return True
    except Exception as e:
        print(f"✗ Chyba při vytváření zálohy: {e}")
        return False


def list_backups():
    """Seznam všech záloh."""
    ensure_backup_dir()

    backups = sorted(BACKUP_DIR.glob("pruvodky_backup_*.db"), reverse=True)

    if not backups:
        print("Žádné zálohy nenalezeny.")
        return

    print(f"{'Název':<40} {'Velikost':>12} {'Datum':<25}")
    print("-" * 80)

    for backup in backups:
        stat = backup.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M:%S")
        print(f"{backup.name:<40} {size:>12,} {mtime:<25}")

    print(f"\nCelkem: {len(backups)} záloh")


def restore_database(backup_file=None):
    """Obnoví databázi ze zálohy."""
    ensure_backup_dir()

    if backup_file:
        backup_path = BACKUP_DIR / backup_file
        if not backup_path.exists():
            # Zkusíme najít soubor
            matches = list(BACKUP_DIR.glob(backup_file))
            if matches:
                backup_path = matches[0]
            else:
                print(f"✗ Záloha nenalezena: {backup_file}")
                return False
    else:
        # Najít nejnovější zálohu
        backups = sorted(BACKUP_DIR.glob("pruvodky_backup_*.db"), reverse=True)
        if not backups:
            print("✗ Žádné zálohy k dispozici.")
            return False
        backup_path = backups[0]

    if not backup_path.exists():
        print(f"✗ Soubor zálohy neexistuje: {backup_path}")
        return False

    # Vytvořit rezervní kopii aktuální databáze před obnovením
    if DB_PATH.exists():
        emergency_backup = BASE_DIR / f"pruvodky_emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_PATH, emergency_backup)
        print(f"✓ Vytvořena nouzová záloha: {emergency_backup}")

    try:
        shutil.copy2(backup_path, DB_PATH)
        print(f"✓ Databáze obnovena z: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Chyba při obnově databáze: {e}")
        return False


def cleanup_old_backups(days=7):
    """Smazat staré zálohy."""
    ensure_backup_dir()

    cutoff_date = datetime.now() - timedelta(days=days)
    backups = list(BACKUP_DIR.glob("pruvodky_backup_*.db"))

    deleted = 0
    for backup in backups:
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        if mtime < cutoff_date:
            try:
                backup.unlink()
                print(f"  Smazáno: {backup.name}")
                deleted += 1
            except Exception as e:
                print(f"  ✗ Nelze smazat {backup.name}: {e}")

    print(f"\n✓ Smazáno {deleted} starých záloh (> {days} dní)")
    return deleted


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nPoužití: python backup_db.py <prikaz> [parametr]")
        print("\nPříkazy:")
        print("  backup          Vytvořit novou zálohu")
        print("  restore [file]  Obnovit z zálohy (nebo z posledního)")
        print("  list            Seznam všech záloh")
        print("  cleanup [days]  Smazat staré zálohy (výchozí 7 dní)")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "backup":
        success = backup_database()
        sys.exit(0 if success else 1)

    elif command == "restore":
        backup_file = sys.argv[2] if len(sys.argv) > 2 else None
        success = restore_database(backup_file)
        sys.exit(0 if success else 1)

    elif command == "list":
        list_backups()

    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        cleanup_old_backups(days)

    else:
        print(f"Neznámý příkaz: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
