# Generátor průvodek a štítků

Webová aplikace pro generování průvodek a štítků v PDF formátu.

## Funkcionality

- **Průvodka Stroje** - Generování průvodky pro výrobní stroje (A4 formát)
- **Průvodka Svařovna** - Generování průvodky pro svařovnu s kategoriemi (A5 formát)
- **Štítky** - Generování štítků různých velikostí (A5, A6, custom)
- **Archiv dokumentů** - Ukládání a správa vygenerovaných PDF
- **Správa šablon** - Možnost vytvářet a upravovat šablony (pro admin/mistr)
- **Správa uživatelů** - Administrace uživatelů s rolemi (admin)

## Role uživatelů

| Rol<span>e</span>       | Popis                                              |
|-------------------------|----------------------------------------------------|
| **viewer**              | Jen prohlížení archivu                             |
| **operátor**            | Generování dokumentů                               |
| **mistr**               | Generování + správa šablon                         |
| **admin**               | Plný přístup včetně správy uživatelů               |

## Instalace

### Požadavky

- Python 3.10+
- pip (Python package manager)

### Postup

1. Nainstalujte závislosti:
   ```bash
   pip install -r requirements.txt
   ```

2. Spusťte aplikaci:
   ```bash
   python run.py
   ```

3. Otevřete prohlížeč na adrese: http://localhost:5000

4. Přihlaste se výchozími údaji:
   - Uživatel: `admin`
   - Heslo: `admin123`

5. **DŮLEŽITÉ:** Změňte výchozí heslo po prvním přihlášení!

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
