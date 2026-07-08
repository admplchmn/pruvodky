# Harmonogram projektu - Generátor průvodek

## Přehled fází projektu

### Fáze 1: Základní infrastruktura (Dokončeno) ✅
- [x] Nastavení Flask aplikace
- [x] Databázové modely (User, Document, Template)
- [x] Autentizace a autorizace (login, role-based access)
- [x] Git repozitář nastaven
- [x] Základní HTML templaty

### Fáze 2: Generování dokumentů (V proběhu) 🔄
- [x] PDF generování pro Stroje (průvodky A4)
- [x] PDF generování pro Svařovnu (průvodky A5)
- [x] PDF generování štítků
- [ ] Testování generování PDF s českými znaky
- [ ] Optimalizace layoutu podle originálních skriptů

### Fáze 3: Správa šablon (Částečně hotovo)
- [x] Model Template vytvořen
- [x] Ruty pro CRUD operace
- [ ] UI pro editaci šablon vylepšeno
- [ ] Preddefinované šablony

### Fáze 4: Archivace a vyhledávání (Hotovo) ✅
- [x] Ukládání dokumentů do databáze
- [x] Seznam archivovaných dokumentů
- [x] Filtrace podle typu, výrobního čísla, data
- [x] Stahování a prohlížení PDF
- [ ] Hromadný export dokumentů

### Fáze 5: Nasazení a testování (Plánováno)
- [ ] Testovací scénáře
- [ ] Dokumentace nasazení
- [ ] Production konfigurace
- [ ] Backup strategie

---

## Detailní rozdělení práce

### Týden 1-2: Základy
| Úkol | Stav | Poznámka |
|------|------|----------|
| Flask app skeleton | ✅ | Hotovo |
| User authentication | ✅ | Hotovo |
| Database models | ✅ | Hotovo |
| Basic templates | ✅ | Bootstrap 5 |

### Týden 3-4: Generování PDF
| Úkol | Stav | Poznámka |
|------|------|----------|
| Průvodka Stroje A4 | ✅ | Code39 barcode |
| Průvodka Svařovna A5 | ✅ | Code128 barcode |
| Štítky A5/A6 | ✅ | Více velikostí |
| Čeština v PDF | ⚠️ | Testovat fonty |

### Týden 5-6: Správa obsahu
| Úkol | Stav | Poznámka |
|------|------|----------|
| Šablony CRUD | ✅ | Základ funkční |
| Archiv dokumentů | ✅ | S filtry |
| Vyhledávání | ✅ | Podle PN, data |

### Týden 7-8: Nasazení
| Úkol | Stav | Poznámka |
|------|------|----------|
| Testing | 📋 | Plánováno |
| Documentation | 📋 | Plánováno |
| Production deploy | 📋 | Plánováno |

---

## Technologie

| Složka | Technologie |
|--------|-------------|
| Backend | Python 3.9+, Flask |
| Database | SQLite (production: PostgreSQL volitelné) |
| Frontend | Bootstrap 5, Jinja2 |
| PDF | ReportLab |
| Auth | Flask-Login, Werkzeug |
| Deployment | Gunicorn + Nginx (volitelné) |

---

## Status aktuální verze

**Verze:** 0.9.0-dev
**Datum:** 2026-07-08

**Funkční:**
- Přihlašování uživatelů
- Role-based přístup (admin, mistr, operátor)
- Generování průvodek Stroje (A4)
- Generování průvodek Svařovna (A5, více stran)
- Generování štítků (A5, A6)
- Archivace všech dokumentů
- Základní správa šablon

**Následující kroky:**
1. Testování PDF generování s českými znaky
2. Vylepšení UI/UX
3. Přidání preddefinovaných šablon
4. Dokumentace nasazení
