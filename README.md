# Generátor průvodek a štítků

Webová aplikace pro generování průvodek, štítků a správu dokumentů ve výrobním prostředí.

## Funkcionality

- **Generování průvodek** - Pro stroje (A4) a svařovnu (A5)
- **Generování štítků** - Více velikostí (A5, A6)
- **Správa šablon** - Ukládání a editace často používaných šablon
- **Správa uživatelů** - Role-based přístup (admin, mistr, operátor)
- **Archivace dokumentů** - Historie všech vygenerovaných dokumentů s vyhledáváním

## Rychlý start

### Instalace

```bash
# Klonujte repozitář
git clone https://github.com/admplchmn/pruvodky.git
cd pruvodky

# Vytvořte virtuální prostředí
python -m venv venv
source venv/bin/activate  # Linux/Mac
# nebo venv\Scripts\activate  # Windows

# Nainstalujte závislosti
pip install -r requirements.txt

# Spusťte aplikaci
python run.py
```

### Přihlášení

Otevřete prohlížeč na `http://localhost:5000`

Výchozí administrátorský účet:
- **Uživatelské jméno:** `admin`
- **Heslo:** `admin123`

⚠️ **Důležité:** Změňte heslo po prvním přihlášení!

## Role uživatelů

| Role       | Popis                                              |
|------------|----------------------------------------------------|
| **viewer** | Jen prohlížení archivu                             |
| **operátor** | Generování dokumentů                             |
| **mistr**  | Generování + správa šablon                         |
| **admin**  | Plný přístup včetně správy uživatelů               |

## Použití

### Generování průvodky Stroje
1. Přihlaste se do aplikace
2. Klikněte na "Průvodka Stroje"
3. Vyplňte formulář (výrobní číslo, stroj, datum, jméno, operace)
4. Klikněte "Vygenerovat PDF"

### Generování průvodky Svařovna
1. Přihlaste se do aplikace
2. Klikněte na "Průvodka Svařovna"
3. Vyplňte formulář (stroj, kategorie, výrobní číslo, datum, jméno)
4. Kategorie automaticky určuje seznam operací
5. Klikněte "Vygenerovat PDF"

### Archivace
- Všechny vygenerované dokumenty se automaticky ukládají do archivu
- Archiv je dostupný pro všechny přihlášené uživatele
- Admini mohou dokumenty mazat

## Production nasazení

Pro production doporučujeme:

1. **Použít Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
   ```

2. **Změnit SECRET_KEY** v config.py na silné náhodné hodnotu

3. **Nastavit Nginx** jako reverse proxy (volitelné)

## Struktura projektu

```
pruvodky_app/
├── app.py              # Hlavní aplikace Flask
├── config.py           # Konfigurace
├── models.py           # Databázové modely
├── auth.py             # Autentizace a autorizace
├── pdf_utils.py        # Nástroje pro generování PDF
├── run.py              # Spouštěcí skript
├── requirements.txt    # Seznam závislostí
├── templates/          # HTML šablony
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── change_password.html
│   ├── pruvodka_stroje.html
│   ├── pruvodka_svarovna.html
│   ├── stitky.html
│   ├── archiv.html
│   ├── sablony.html
│   ├── sablony_create.html
│   ├── sablony_edit.html
│   └── admin/
│       ├── users.html
│       ├── create_user.html
│       └── edit_user.html
├── static/             # Statické soubory (CSS, JS)
└── uploads/            # Uploadované soubory
```

## Databáze

Aplikace používá SQLite databázi (`pruvodky.db`), která se vytvoří automaticky při prvním spuštění.

### Tabulky

- **users** - Uživatelé systému
- **templates** - Šablony pro generování
- **documents** - Archivované dokumenty (PDF)

## Technologie

- **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite
- **PDF:** ReportLab
- **Frontend:** HTML5, CSS3, Jinja2

## Licence

Vnitřní použití společnosti.
