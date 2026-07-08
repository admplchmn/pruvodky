"""
Nástroje pro generování PDF - přeneseno ze skriptů Pruvodka_Stroje.py a SVAR_pruvodky.py
"""
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4, A5, A6
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code39, code128
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ============================================================================
# FONTY (čeština)
# ============================================================================

def register_fonts():
    """Registrace českých fontů (Arial)."""
    try:
        # Windows
        font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        arial = font_dir / "arial.ttf"
        arial_bold = font_dir / "arialbd.ttf"

        if arial.exists():
            pdfmetrics.registerFont(TTFont("ArialCZ", str(arial)))
        if arial_bold.exists():
            pdfmetrics.registerFont(TTFont("ArialCZ-Bold", str(arial_bold)))
    except Exception:
        pass


def get_font(normal=True):
    """Vrátí název fontu (normal nebo bold)."""
    if normal:
        return "ArialCZ" if "ArialCZ" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    else:
        return "ArialCZ-Bold" if "ArialCZ-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"


# ============================================================================
# BARCODES
# ============================================================================

def make_barcode_code39(text: str):
    """Vytvoří Code39 barcode."""
    return code39.Standard39(text, barHeight=18 * mm, stop=1, checksum=0)


def make_barcode_code128(text: str, height_mm=20, width_mm=0.32):
    """Vytvoří Code128 barcode."""
    return code128.Code128(text, barHeight=height_mm * mm, barWidth=width_mm * mm)


def draw_barcode(c, barcode, x, y, scale=2.0):
    """Vykreslí barcode na pozici x, y."""
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    barcode.drawOn(c, 0, 0)
    c.restoreState()


def draw_centered_barcode(c, barcode, y, page_width, height_mm=20, width_mm=0.32):
    """Vykreslí barcode uprostřed stránky."""
    x = (page_width - barcode.width) / 2
    barcode.drawOn(c, x, y)


# ============================================================================
# POMOCNÉ FUNKCE
# ============================================================================

def safe_filename(text: str) -> str:
    """Vytvoří bezpečný název souboru."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("_") or "document"


OPERATIONS_STROJE = {
    "Obrobna": "-T",
    "Svařovna": "-S",
    "Ohranování": "-O",
    "Lasery": "-D",
    "Lakovna": "-L",
    "Montáž": "-M",
    "Elektromontáž": "-E",
    "SW": "-SW",
}


CATEGORIES_SVAROVNA = {
    "SP, A": [
        "Kostra", "Bočnice kostry", "Agregát", "Oplechování kostry",
        "Sváření oplechování", "Stůl", "Příslušenství",
    ],
    "R, SR": [
        "Kostra", "Agregát", "Oplechování kostry", "Sváření oplechování",
        "Stoly", "Příslušenství",
    ],
    "SC": [
        "Kostra", "Agregát", "Oplechování kostry", "Sváření oplechování",
        "Stoly", "Bočnice kostry", "Příslušenství",
    ],
    "TWINGO": [
        "Kostra", "Agregáty", "Oplechování kostry", "Sváření oplechování",
        "Stůl", "Příslušenství",
    ],
    "CNC": [
        "Spodní podstavec", "Sloupy", "Portál", "Oplechování",
        "Saně", "Smykadlo", "Zásobník", "Odsávání", "Kabina", "Ovládací pult",
    ],
    "F250": [
        "Kostra", "Agregát", "Oplechování kostry", "Sváření oplechování",
        "Stůl", "Kryt vřetene", "Příslušenství",
    ],
    "SF": [
        "Kostra", "Agregát", "Oplechování kostry", "Sváření oplechování",
        "Stůl", "Kryt vřetene", "Příslušenství",
    ],
    "Agregáty SPB": ["Agregát"],
    "B3, B5, JSM": [
        "Kostra", "Bočnice kostry", "Oplechování kostry", "Sváření oplechování",
        "Stůl", "Oplechování stolu", "Příslušenství", "Vývěva", "Ometáky",
    ],
    "B7": [
        "Horní rám", "Oplechování kostry", "Sváření oplechování", "Stůl",
        "Oplechování stolu", "Příslušenství", "Spodní rám", "Vývěva", "Ometáky",
    ],
    "Final": [
        "Kostra", "Oplechování kostry", "Sváření oplechování", "Stůl",
        "Oplechování stolu", "Příslušenství", "Sváření bočnice", "Agregáty", "Vývěva", "Ometáky",
    ],
    "Pony": [
        "Kostra", "Bočnice kostry", "Oplechování kostry", "Sváření oplechování",
        "Stůl", "Oplechování stolu", "Příslušenství",
    ],
    "Cindy": [
        "Kostra", "Oplechování kostry", "Sváření oplechování", "Stůl",
        "Oplechování stolu", "Příslušenství", "Agregát",
    ],
    "Duplex": [
        "Horní rám", "Oplechování zadní kostry", "Sváření oplechování", "Stůl",
        "Oplechování stolu", "Příslušenství", "Spodní rám", "Zadní kostra",
        "Oplechování přední kostry", "Vývěva", "Ometáky",
    ],
    "VD20, VD26": [
        "Kostra", "Pojezdové stolky", "Oplechování", "Stůl", "Příslušenství",
    ],
    "Basset, Husky, PBB": [
        "Kostra", "Oplechování", "Stůl", "Příslušenství", "Bočnice kostry", "Vrchní sklopný stůl",
    ],
    "Fox, PBM": [
        "Kostra", "Oplechování", "Stůl", "Příslušenství", "Bočnice kostry",
        "Příčník", "Rotační stůl + stojan",
    ],
    "HB1000, HBK3200": [
        "Kostra", "Oplechování", "Stůl / stoly", "Příslušenství", "Agregát",
    ],
}


OP_CODE_MAP = {
    "Kostra": "KOSTRA",
    "Bočnice kostry": "BOCNICE-KOSTRY",
    "Agregát": "AGREGAT",
    "Agregáty": "AGREGATY",
    "Oplechování kostry": "OPLE-KOSTRY",
    "Oplechování zadní kostry": "OPLE-Z-KOSTRY",
    "Oplechování přední kostry": "OPLE-P-KOSTRY",
    "Sváření oplechování": "SVAR-OPLE",
    "Sváření bočnice": "SVAR-BOCNICE",
    "Stůl": "STUL",
    "Stoly": "STOLY",
    "Stůl / stoly": "STUL-STOLY",
    "Oplechování stolu": "OPLE-STOLU",
    "Příslušenství": "PRISL",
    "Vývěva": "VYVEVA",
    "Ometáky": "OMETAKY",
    "Horní rám": "HORNI-RAM",
    "Spodní rám": "SPODNI-RAM",
    "Zadní kostra": "ZADNI-KOSTRA",
    "Pojezdové stolky": "POJEZD-STOLKY",
    "Oplechování": "OPLE",
    "Vrchní sklopný stůl": "VRCH-SKLOP-STUL",
    "Příčník": "PRICNIK",
    "Rotační stůl + stojan": "ROT-STUL-STOJAN",
    "Spodní podstavec": "SPOD-PODST",
    "Sloupy": "SLOUPY",
    "Portál": "PORTAL",
    "Saně": "SANE",
    "Smykadlo": "SMYKADLO",
    "Zásobník": "ZASOBNIK",
    "Odsávání": "ODSAVANI",
    "Kabina": "KABINA",
    "Ovládací pult": "OVL-PULT",
    "Kryt vřetene": "KRYT-VRETENE",
}


def op_code(operation: str) -> str:
    """Převod operace na kód pro barcode."""
    if operation in OP_CODE_MAP:
        return OP_CODE_MAP[operation]
    text = unicodedata.normalize("NFKD", operation).encode("ascii", "ignore").decode("ascii")
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", "-", text)
    return text.strip("-")
