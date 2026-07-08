#!/usr/bin/env python3
"""
Testovací skript pro ověření PDF generování a českých fontů.
Spusťte: python test_pdf_generation.py
"""

import os
import sys
from io import BytesIO

# Přidáme cestu k projektu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from pdf_utils import (
    register_fonts, get_font, make_barcode_code39,
    make_barcode_code128, CATEGORIES_SVAROVNA, op_code
)


def test_font_registration():
    """Test registrace českých fontů."""
    print("=" * 60)
    print("TEST 1: Registrace fontů")
    print("=" * 60)

    register_fonts()

    normal_font = get_font(normal=True)
    bold_font = get_font(normal=False)

    print(f"Normal font: {normal_font}")
    print(f"Bold font: {bold_font}")

    if "ArialCZ" in normal_font:
        print("✓ Čeština je podporována!")
    else:
        print("⚠ Čeština NENÍ podporována - použity jsou základní fonty")

    return True


def test_pruvodka_stroje_pdf():
    """Test generování průvodky Stroje."""
    print("\n" + "=" * 60)
    print("TEST 2: Průvodka Stroje (A4)")
    print("=" * 60)

    from app import create_pruvodka_stroje_pdf

    try:
        pdf_buffer = create_pruvodka_stroje_pdf(
            datum="08.07.2026",
            jmeno="Jan Novák",
            vyrobni="TEST-12345",
            stroj="CNC-FRÁZA-01",
            operace="Obrobna"
        )

        pdf_data = pdf_buffer.getvalue()
        output_file = "test_pruvodka_stroje.pdf"

        with open(output_file, "wb") as f:
            f.write(pdf_data)

        print(f"✓ PDF bylo úspěšně vygenerováno: {output_file}")
        print(f"  Velikost: {len(pdf_data)} bajtů")
        return True

    except Exception as e:
        print(f"✗ Chyba při generování PDF: {e}")
        return False


def test_pruvodka_svarovna_pdf():
    """Test generování průvodky Svařovna."""
    print("\n" + "=" * 60)
    print("TEST 3: Průvodka Svařovna (A5)")
    print("=" * 60)

    from app import create_pruvodka_svarovna_pdf

    try:
        pdf_buffer = create_pruvodka_svarovna_pdf(
            machine="SVAŘOVACÍ-STŮL-02",
            category="SP, A",
            order="SVAR-67890",
            date="08.07.2026",
            name="Petr Svářeč"
        )

        pdf_data = pdf_buffer.getvalue()
        output_file = "test_pruvodka_svarovna.pdf"

        with open(output_file, "wb") as f:
            f.write(pdf_data)

        operations = CATEGORIES_SVAROVNA.get("SP, A", [])
        print(f"✓ PDF bylo úspěšně vygenerováno: {output_file}")
        print(f"  Velikost: {len(pdf_data)} bajtů")
        print(f"  Počet stran (operací): {len(operations)}")
        return True

    except Exception as e:
        print(f"✗ Chyba při generování PDF: {e}")
        return False


def test_stitek_pdf():
    """Test generování štítku."""
    print("\n" + "=" * 60)
    print("TEST 4: Štítek (A5/A6)")
    print("=" * 60)

    from app import create_stitek_pdf

    try:
        # Test A5
        pdf_buffer_a5 = create_stitek_pdf(
            vyrobni="STITEK-001",
            stroj="TEST-STROJ",
            nazev="ZKOUŠEČKA ŠTÍTEK",
            datum="08.07.2026",
            velikost='A5'
        )

        with open("test_stitek_A5.pdf", "wb") as f:
            f.write(pdf_buffer_a5.getvalue())

        # Test A6
        pdf_buffer_a6 = create_stitek_pdf(
            vyrobni="STITEK-002",
            stroj="TEST-STROJ",
            nazev="MALÝ ŠTÍTEK",
            datum="08.07.2026",
            velikost='A6'
        )

        with open("test_stitek_A6.pdf", "wb") as f:
            f.write(pdf_buffer_a6.getvalue())

        print("✓ Štítky byly úspěšně vygenerovány:")
        print("  - test_stitek_A5.pdf")
        print("  - test_stitek_A6.pdf")
        return True

    except Exception as e:
        print(f"✗ Chyba při generování štítků: {e}")
        return False


def test_barcode_generation():
    """Test generování barcode."""
    print("\n" + "=" * 60)
    print("TEST 5: Generování barcode")
    print("=" * 60)

    try:
        # Code39
        bc39 = make_barcode_code39("TEST-123")
        print(f"✓ Code39 barcode vytvořen: TEST-123")

        # Code128
        bc128 = make_barcode_code128("TEST-456")
        print(f"✓ Code128 barcode vytvořen: TEST-456")

        # Op code mapping
        test_ops = ["Kostra", "Stůl", "Oplechování kostry"]
        for op in test_ops:
            code = op_code(op)
            print(f"  {op} -> {code}")

        return True

    except Exception as e:
        print(f"✗ Chyba při generování barcode: {e}")
        return False


def test_database():
    """Test databázového připojení."""
    print("\n" + "=" * 60)
    print("TEST 6: Databázové připojení")
    print("=" * 60)

    try:
        app = create_app()

        with app.app_context():
            from models import db, User, Document, Template

            # Zkontrolovat tabulky
            tables = db.metadata.tables.keys()
            print(f"✓ Tabulky v databázi: {', '.join(tables)}")

            # Zkontrolovat admina
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"✓ Admin uživatel existuje: {admin.username} ({admin.role})")
            else:
                print("⚠ Admin uživatel neexistuje - bude vytvořen při příštím spuštění")

            return True

    except Exception as e:
        print(f"✗ Chyba databáze: {e}")
        return False


def main():
    """Spustit všechny testy."""
    print("\n" + "=" * 60)
    print("TESTOVÁNÍ APLIKACE PRUVODKY")
    print("=" * 60)

    results = []

    results.append(("Font registration", test_font_registration()))
    results.append(("Barcode generation", test_barcode_generation()))
    results.append(("Průvodka Stroje PDF", test_pruvodka_stroje_pdf()))
    results.append(("Průvodka Svařovna PDF", test_pruvodka_svarovna_pdf()))
    results.append(("Štítek PDF", test_stitek_pdf()))
    results.append(("Database connection", test_database()))

    print("\n" + "=" * 60)
    print("VÝSLEDKY TESTŮ")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nCelkem: {passed}/{total} testů prošlo")

    if passed == total:
        print("\n🎉 Všechny testy prošly!")
        return 0
    else:
        print(f"\n⚠ {total - passed} testů selhalo.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
