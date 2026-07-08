"""
Hlavní aplikace - Generátor průvodek a štítků
"""
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User
from auth import login_required, admin_required, master_required, can_operate_required


def create_app(config_class=Config):
    """Factory function pro vytvoření aplikace."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initializace rozšíření
    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Pro přístup k této stránce je nutné se přihlásit.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Vytvoření databáze a tabulek
    with app.app_context():
        db.create_all()
        # Vytvořit výchozí admina pokud neexistuje
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@pruvodky.local',
                full_name='Administrátor',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')  # Změnit po prvním přihlášení!
            db.session.add(admin)
            db.session.commit()
            print("Vytvořen výchozí uživatel: admin / admin123")

    # ========================================================================
    # ROUTY
    # ========================================================================

    @app.route('/')
    def index():
        """Hlavní stránka s dashboardem."""
        from models import Document, User, Template
        from datetime import datetime, timedelta

        if not current_user.is_authenticated:
            return render_template('index.html', stats=None)

        # Statistiky
        total_documents = Document.query.count()
        total_users = User.query.filter_by(is_active=True).count()
        total_templates = Template.query.count()

        # Dokumenty za posledních 7 dní
        week_ago = datetime.utcnow() - timedelta(days=7)
        documents_this_week = Document.query.filter(Document.created_at >= week_ago).count()

        # Dokumenty podle typu
        doc_types = db.session.query(
            Document.document_type,
            db.func.count(Document.id)
        ).group_by(Document.document_type).all()

        # Poslední dokumenty
        recent_docs = Document.query.order_by(Document.created_at.desc()).limit(5).all()

        stats = {
            'total_documents': total_documents,
            'total_users': total_users,
            'total_templates': total_templates,
            'documents_this_week': documents_this_week,
            'doc_types': dict(doc_types),
            'recent_docs': recent_docs
        }

        return render_template('index.html', stats=stats)

    # Auth routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Přihlášení uživatele."""
        from flask import redirect, url_for, flash, request
        from werkzeug.security import check_password_hash

        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)

            user = User.query.filter_by(username=username).first()

            if user and user.is_active and user.check_password(password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                flash(f'Vítejte, {user.full_name or user.username}!', 'success')
                return redirect(next_page or url_for('index'))
            else:
                flash('Neplatné jméno uživatele nebo heslo.', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Odhlášení uživatele."""
        logout_user()
        flash('Byli jste odhlášeni.', 'info')
        return redirect(url_for('login'))

    @app.route('/profile')
    @login_required
    def profile():
        """Profil uživatele."""
        return render_template('profile.html')

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        """Změna hesla."""
        if request.method == 'POST':
            current_pass = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not current_pass or not new_password or not confirm_password:
                flash('Vyplňte všechna pole.', 'warning')
                return render_template('change_password.html')

            if not current_user.check_password(current_pass):
                flash('Současné heslo je nesprávné.', 'danger')
                return render_template('change_password.html')

            if len(new_password) < 6:
                flash('Nové heslo musí mít alespoň 6 znaků.', 'warning')
                return render_template('change_password.html')

            if new_password != confirm_password:
                flash('Nová hesla se neshodují.', 'danger')
                return render_template('change_password.html')

            current_user.set_password(new_password)
            db.session.commit()
            flash('Heslo bylo úspěšně změněno.', 'success')
            return redirect(url_for('profile'))

        return render_template('change_password.html')

    # Admin routes - Správa uživatelů
    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """Seznam všech uživatelů (admin only)."""
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('admin/users.html', users=users)

    @app.route('/admin/users/create', methods=['GET', 'POST'])
    @admin_required
    def admin_create_user():
        """Vytvoření nového uživatele."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            full_name = request.form.get('full_name', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', 'operátor')

            if not username or not password:
                flash('Uživatelské jméno a heslo jsou povinné.', 'warning')
                return render_template('admin/create_user.html')

            if User.query.filter_by(username=username).first():
                flash('Uživatelské jméno již existuje.', 'danger')
                return render_template('admin/create_user.html')

            user = User(
                username=username,
                email=email or None,
                full_name=full_name or None,
                role=role,
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'Uživatel {username} byl vytvořen.', 'success')
            return redirect(url_for('admin_users'))

        return render_template('admin/create_user.html')

    @app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def admin_edit_user(user_id):
        """Úprava uživatele."""
        user = User.query.get_or_404(user_id)

        if request.method == 'POST':
            user.email = request.form.get('email', '').strip() or None
            user.full_name = request.form.get('full_name', '').strip() or None
            user.role = request.form.get('role', 'operátor')
            user.is_active = request.form.get('is_active', False) == 'on'

            new_password = request.form.get('password', '').strip()
            if new_password:
                if len(new_password) < 6:
                    flash('Heslo musí mít alespoň 6 znaků.', 'warning')
                    return render_template('admin/edit_user.html', user=user)
                user.set_password(new_password)

            db.session.commit()
            flash('Uživatel byl aktualizován.', 'success')
            return redirect(url_for('admin_users'))

        return render_template('admin/edit_user.html', user=user)

    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @admin_required
    def admin_delete_user(user_id):
        """Smazání uživatele (soft delete)."""
        user = User.query.get_or_404(user_id)

        if user.username == 'admin':
            flash('Nelze smazat hlavního administrátora.', 'danger')
            return redirect(url_for('admin_users'))

        if user.id == current_user.id:
            flash('Nemůžete smazat sami sebe.', 'danger')
            return redirect(url_for('admin_users'))

        user.is_active = False
        db.session.commit()
        flash(f'Uživatel {user.username} byl deaktivován.', 'success')
        return redirect(url_for('admin_users'))

    # Průvodky Stroje routes
    @app.route('/pruvodka/stroje', methods=['GET', 'POST'])
    @can_operate_required
    def pruvodka_stroje():
        """Generování průvodky pro stroje."""
        from pdf_utils import create_pruvodka_stroje_pdf
        from datetime import datetime
        import io

        if request.method == 'POST':
            vyrobni = request.form.get('vyrobni', '').strip()
            stroj = request.form.get('stroj', '').strip()
            datum = request.form.get('datum', '').strip()
            jmeno = request.form.get('jmeno', '').strip() or current_user.full_name or current_user.username
            operace = request.form.get('operace', 'Obrobna')

            if not vyrobni:
                flash('Vyplňte výrobní číslo / kooperaci.', 'warning')
                return render_template('pruvodka_stroje.html')

            if not stroj:
                flash('Vyplňte stroj.', 'warning')
                return render_template('pruvodka_stroje.html')

            if not datum:
                flash('Vyplňte datum.', 'warning')
                return render_template('pruvodka_stroje.html')

            if not jmeno:
                flash('Vyplňte jméno.', 'warning')
                return render_template('pruvodka_stroje.html')

            # Generování PDF
            pdf_buffer = create_pruvodka_stroje_pdf(
                datum=datum,
                jmeno=jmeno,
                vyrobni=vyrobni,
                stroj=stroj,
                operace=operace
            )

            # Uložení do databáze
            from models import Document
            doc = Document(
                document_type='pruvodka_stroje',
                title=f'Průvodka {vyrobni} - {operace}',
                production_number=vyrobni,
                machine=stroj,
                operation=operace,
                pdf_data=pdf_buffer.getvalue(),
                created_by=current_user.id
            )
            db.session.add(doc)
            db.session.commit()

            flash('Průvodka byla vygenerována a uložena.', 'success')

            # Vrácení PDF k stažení
            from flask import Response
            pdf_buffer.seek(0)
            return Response(
                pdf_buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="{vyrobni}.pdf"'
                }
            )

        return render_template('pruvodka_stroje.html')

    # Průvodka Svařovna routes
    @app.route('/pruvodka/svarovna', methods=['GET', 'POST'])
    @can_operate_required
    def pruvodka_svarovna():
        """Generování průvodky pro svařovnu."""
        from pdf_utils import create_pruvodka_svarovna_pdf, CATEGORIES_SVAROVNA
        import io

        categories = list(CATEGORIES_SVAROVNA.keys())

        if request.method == 'POST':
            stroj = request.form.get('stroj', '').strip()
            category = request.form.get('category', '')
            vyrobni = request.form.get('vyrobni', '').strip()
            datum = request.form.get('datum', '').strip()
            jmeno = request.form.get('jmeno', '').strip() or current_user.full_name or current_user.username

            if not stroj:
                flash('Vyplňte stroj.', 'warning')
                return render_template('pruvodka_svarovna.html', categories=categories)

            if not category:
                flash('Vyberte kategorii.', 'warning')
                return render_template('pruvodka_svarovna.html', categories=categories)

            if not vyrobni:
                flash('Vyplňte výrobní číslo / kooperaci.', 'warning')
                return render_template('pruvodka_svarovna.html', categories=categories)

            if not datum:
                flash('Vyplňte datum.', 'warning')
                return render_template('pruvodka_svarovna.html', categories=categories)

            if not jmeno:
                flash('Vyplňte jméno.', 'warning')
                return render_template('pruvodka_svarovna.html', categories=categories)

            # Generování PDF
            pdf_buffer = create_pruvodka_svarovna_pdf(
                machine=stroj,
                category=category,
                order=vyrobni,
                date=datum,
                name=jmeno
            )

            # Uložení do databáze
            from models import Document
            operations = CATEGORIES_SVAROVNA[category]
            doc = Document(
                document_type='pruvodka_svarovna',
                title=f'Průvodka Svařovna {vyrobni} - {category}',
                production_number=vyrobni,
                machine=stroj,
                category=category,
                operation=', '.join(operations[:3]) + '...',  # První 3 operace
                pdf_data=pdf_buffer.getvalue(),
                extra_data={'operations': operations},
                created_by=current_user.id
            )
            db.session.add(doc)
            db.session.commit()

            flash('Průvodka byla vygenerována a uložena.', 'success')

            # Vrácení PDF k stažení
            from flask import Response
            pdf_buffer.seek(0)
            filename = f"pruvodka_{vyrobni}_{category}.pdf"
            return Response(
                pdf_buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )

        return render_template('pruvodka_svarovna.html', categories=categories)

    # Štítky routes
    @app.route('/stitky', methods=['GET', 'POST'])
    @can_operate_required
    def stitky():
        """Generování štítků."""
        from pdf_utils import create_stitek_pdf
        import io

        if request.method == 'POST':
            vyrobni = request.form.get('vyrobni', '').strip()
            stroj = request.form.get('stroj', '').strip()
            nazev = request.form.get('nazev', '').strip()
            datum = request.form.get('datum', '').strip()
            velikost = request.form.get('velikost', 'A5')  # A5, A6, custom

            if not vyrobni:
                flash('Vyplňte výrobní číslo.', 'warning')
                return render_template('stitky.html')

            if not nazev:
                flash('Vyplňte název štítku.', 'warning')
                return render_template('stitky.html')

            # Generování PDF
            pdf_buffer = create_stitek_pdf(
                vyrobni=vyrobni,
                stroj=stroj,
                nazev=nazev,
                datum=datum,
                velikost=velikost
            )

            # Uložení do databáze
            from models import Document
            doc = Document(
                document_type='stitek',
                title=f'Stítek {nazev} - {vyrobni}',
                production_number=vyrobni,
                machine=stroj,
                extra_data={'velikost': velikost, 'nazev': nazev},
                pdf_data=pdf_buffer.getvalue(),
                created_by=current_user.id
            )
            db.session.add(doc)
            db.session.commit()

            flash('Štítek byl vygenerován a uložen.', 'success')

            # Vrácení PDF k stažení
            from flask import Response
            pdf_buffer.seek(0)
            return Response(
                pdf_buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="stitek_{vyrobni}.pdf"'
                }
            )

        return render_template('stitky.html')

    # Archivace dokumentů
    @app.route('/archiv')
    @login_required
    def archiv():
        """Seznam archivovaných dokumentů."""
        from models import Document

        # Filtry
        document_type = request.args.get('type', '')
        production_number = request.args.get('production_number', '').strip()
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        query = Document.query

        if document_type:
            query = query.filter_by(document_type=document_type)
        if production_number:
            query = query.filter(Document.production_number.like(f'%{production_number}%'))
        if date_from:
            from datetime import datetime
            query = query.filter(Document.created_at >= datetime.strptime(date_from, '%d.%m.%Y'))
        if date_to:
            from datetime import datetime, timedelta
            query = query.filter(Document.created_at <= datetime.strptime(date_to, '%d.%m.%Y') + timedelta(days=1))

        documents = query.order_by(Document.created_at.desc()).all()
        return render_template('archiv.html', documents=documents, current_type=document_type)

    @app.route('/archiv/<int:doc_id>/download')
    @login_required
    def download_document(doc_id):
        """Stáhnutí dokumentu z archivu."""
        from models import Document
        from flask import Response

        doc = Document.query.get_or_404(doc_id)

        if not doc.pdf_data:
            flash('Dokument nemá přiložené PDF.', 'danger')
            return redirect(url_for('archiv'))

        return Response(
            doc.pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{doc.title}.pdf"'
            }
        )

    @app.route('/archiv/<int:doc_id>/view')
    @login_required
    def view_document(doc_id):
        """Zobrazení dokumentu v prohlížeči."""
        from models import Document
        from flask import Response

        doc = Document.query.get_or_404(doc_id)

        if not doc.pdf_data:
            flash('Dokument nemá přiložené PDF.', 'danger')
            return redirect(url_for('archiv'))

        return Response(
            doc.pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{doc.title}.pdf"'
            }
        )

    @app.route('/archiv/<int:doc_id>/delete', methods=['POST'])
    @admin_required
    def delete_document(doc_id):
        """Smazání dokumentu z archivu."""
        from models import Document

        doc = Document.query.get_or_404(doc_id)
        db.session.delete(doc)
        db.session.commit()
        flash('Dokument byl smazán.', 'success')
        return redirect(url_for('archiv'))

    # Správa šablon
    @app.route('/sablony')
    @login_required
    def sablony():
        """Seznam šablon."""
        from models import Template
        templates = Template.query.order_by(Template.created_at.desc()).all()
        return render_template('sablony.html', templates=templates)

    @app.route('/sablony/create', methods=['GET', 'POST'])
    @master_required
    def create_template():
        """Vytvoření nové šablony."""
        from models import Template
        import json

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            template_type = request.form.get('template_type', '')
            content_json = request.form.get('content_json', '{}')

            if not name or not template_type:
                flash('Název a typ šablony jsou povinné.', 'warning')
                return render_template('sablony_create.html')

            template = Template(
                name=name,
                template_type=template_type,
                content_json=content_json,
                created_by=current_user.id,
                is_default=False
            )
            db.session.add(template)
            db.session.commit()
            flash('Šablona byla vytvořena.', 'success')
            return redirect(url_for('sablony'))

        return render_template('sablony_create.html')

    @app.route('/sablony/<int:tpl_id>/edit', methods=['GET', 'POST'])
    @master_required
    def edit_template(tpl_id):
        """Úprava šablony."""
        from models import Template

        template = Template.query.get_or_404(tpl_id)

        if request.method == 'POST':
            template.name = request.form.get('name', '').strip()
            template.content_json = request.form.get('content_json', '{}')

            db.session.commit()
            flash('Šablona byla aktualizována.', 'success')
            return redirect(url_for('sablony'))

        return render_template('sablony_edit.html', template=template)

    @app.route('/sablony/<int:tpl_id>/delete', methods=['POST'])
    @master_required
    def delete_template(tpl_id):
        """Smazání šablony."""
        from models import Template

        template = Template.query.get_or_404(tpl_id)
        db.session.delete(template)
        db.session.commit()
        flash('Šablona byla smazána.', 'success')
        return redirect(url_for('sablony'))

    return app


# Helper funkce pro generování PDF (zatím placeholder - bude doplněno)
def create_pruvodka_stroje_pdf(datum, jmeno, vyrobni, stroj, operace):
    """Generuje PDF průvodky pro stroje."""
    from pdf_utils import make_barcode_code39, draw_barcode, get_font, OPERATIONS_STROJE
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from reportlab.lib.units import mm

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    left = 25 * mm
    right = w - 25 * mm
    y = h - 25 * mm

    def hr(line_y):
        c.setLineWidth(1)
        c.line(left, line_y, right, line_y)

    c.setFont(get_font(False), 18)
    c.drawString(left, y, "Průvodka")
    y -= 10 * mm
    hr(y)
    y -= 12 * mm

    c.setFont(get_font(True), 12)
    c.drawString(left, y, f"Datum: {datum}")
    y -= 10 * mm

    c.drawString(left, y, f"Vytvořil: {jmeno}")
    y -= 10 * mm

    c.setFont(get_font(True), 12)
    c.drawString(left, y, "Stroj: ")
    offset = c.stringWidth("Stroj: ", get_font(True), 12)
    c.setFont(get_font(False), 12)
    c.drawString(left + offset, y, stroj)
    y -= 10 * mm

    c.setFont(get_font(True), 12)
    c.drawString(left, y, "Výrobní číslo/kooperace: ")
    offset = c.stringWidth("Výrobní číslo/kooperace: ", get_font(True), 12)
    c.setFont(get_font(False), 12)
    c.drawString(left + offset, y, vyrobni)
    y -= 10 * mm

    hr(y)
    y -= 14 * mm

    c.setFont(get_font(False), 12)
    c.drawString(left, y, f"Operace: {operace}")
    y -= 18 * mm

    bc1 = make_barcode_code39(vyrobni)
    draw_barcode(c, bc1, left + 20 * mm, y - 30 * mm)
    y -= 40 * mm

    c.setFont(get_font(True), 11)
    c.drawString(left + 20 * mm, y, f"Kód: {vyrobni}")
    y -= 12 * mm

    hr(y)
    y -= 18 * mm

    c.setFont(get_font(False), 13)
    c.drawString(left, y, "Konec práce na zakázce:")
    y -= 18 * mm

    suffix = OPERATIONS_STROJE.get(operace, "-X")
    code2 = f"{vyrobni}{suffix}"

    bc2 = make_barcode_code39(code2)
    draw_barcode(c, bc2, left + 20 * mm, y - 30 * mm)
    y -= 40 * mm

    c.setFont(get_font(True), 11)
    c.drawString(left + 20 * mm, y, f"Kód: {code2}")
    y -= 16 * mm

    c.setFont(get_font(True), 12)
    c.drawString(left, y, "Potvrzeno (Jméno mistra):")
    c.line(left + 60 * mm, y - 1, right, y - 1)
    y -= 16 * mm

    c.drawString(left, y, "Poznámka:")

    c.save()
    return buffer


def create_pruvodka_svarovna_pdf(machine, category, order, date, name):
    """Generuje PDF průvodky pro svařovnu."""
    from pdf_utils import (
        make_barcode_code128, draw_centered_barcode, get_font,
        CATEGORIES_SVAROVNA, op_code
    )
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from reportlab.lib.units import mm

    buffer = BytesIO()
    operations = CATEGORIES_SVAROVNA.get(category, [])

    for operation in operations:
        c = canvas.Canvas(buffer, pagesize=A5)
        w, h = A5

        left = 13 * mm
        right = w - 13 * mm
        center = w / 2
        y = h - 18 * mm

        # Nadpis
        c.setFont(get_font(True), 13)
        c.drawCentredString(center, y, f"PRŮVODKA - SVAŘ - {operation}")
        y -= 7 * mm

        c.setLineWidth(1.0)
        c.line(left, y, right, y)
        y -= 10 * mm

        # Data
        c.setFont(get_font(True), 10)
        c.drawString(left + 8 * mm, y, "Stroj:")
        c.setFont(get_font(False), 10)
        c.drawString(left + 62 * mm, y, machine)
        y -= 9 * mm

        c.drawString(left + 8 * mm, y, "Kategorie:")
        c.setFont(get_font(False), 10)
        c.drawString(left + 62 * mm, y, category)
        y -= 9 * mm

        c.drawString(left + 8 * mm, y, "Výrobní číslo/kooperace:")
        c.setFont(get_font(True), 10)
        c.drawString(left + 62 * mm, y, order)
        y -= 9 * mm

        c.drawString(left + 8 * mm, y, "Datum:")
        c.setFont(get_font(True), 10)
        c.drawString(left + 62 * mm, y, date)
        y -= 9 * mm

        c.drawString(left + 8 * mm, y, "Vytvořil:")
        c.setFont(get_font(True), 10)
        c.drawString(left + 62 * mm, y, name)
        y -= 7 * mm

        c.setLineWidth(1.0)
        c.line(left, y, right, y)
        y -= 14 * mm

        # Operace
        c.setFont(get_font(False), 14)
        c.drawCentredString(center, y, f"Operace: {operation}")
        y -= 23 * mm

        # Barcode operace
        base_code = f"{order}--{op_code(operation)}"
        barcode = make_barcode_code128(base_code)
        draw_centered_barcode(c, barcode, y, w, height_mm=20, width_mm=0.32)
        y -= 8 * mm

        c.setFont(get_font(True), 9)
        c.drawCentredString(center, y, f"Kód:  {base_code}")
        y -= 13 * mm

        c.setLineWidth(1.0)
        c.line(left, y, right, y)
        y -= 13 * mm

        # Mistr
        c.setFont(get_font(False), 14)
        c.drawCentredString(center, y, "Potvrzení mistra:")
        y -= 24 * mm

        mistr_code = f"{base_code}-M"
        barcode_mistr = make_barcode_code128(mistr_code)
        draw_centered_barcode(c, barcode_mistr, y, w, height_mm=20, width_mm=0.32)
        y -= 8 * mm

        c.setFont(get_font(True), 9)
        c.drawCentredString(center, y, f"Kód:  {mistr_code}")
        y -= 16 * mm

        c.setFont(get_font(True), 10)
        c.drawString(left + 4 * mm, y, "Podpis mistra:")
        c.line(left + 30 * mm, y - 1 * mm, right - 4 * mm, y - 1 * mm)
        y -= 10 * mm

        c.drawString(left + 4 * mm, y, "Poznámka:")
        c.line(left + 27 * mm, y - 1 * mm, right - 4 * mm, y - 1 * mm)

        c.showPage()

    c.save()
    return buffer


def create_stitek_pdf(vyrobni, stroj, nazev, datum, velikost='A5'):
    """Generuje PDF štítek."""
    from pdf_utils import make_barcode_code128, get_font
    from reportlab.lib.pagesizes import A5, A6
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from reportlab.lib.units import mm

    if velikost == 'A6':
        pagesize = A6
    else:
        pagesize = A5

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=pagesize)
    w, h = pagesize

    left = 10 * mm
    right = w - 10 * mm
    center = w / 2
    y = h - 15 * mm

    # Rámeček
    c.setLineWidth(2)
    c.rect(left, 10 * mm, w - 2 * left, h - 20 * mm)

    # Nadpis
    c.setFont(get_font(False), 16)
    c.drawCentredString(center, y, nazev)
    y -= 12 * mm

    c.setLineWidth(1)
    c.line(left + 5 * mm, y, right - 5 * mm, y)
    y -= 10 * mm

    # Data
    c.setFont(get_font(True), 11)
    c.drawString(left + 5 * mm, y, "Výrobní číslo:")
    c.setFont(get_font(False), 11)
    c.drawString(left + 55 * mm, y, vyrobni)
    y -= 8 * mm

    c.setFont(get_font(True), 11)
    c.drawString(left + 5 * mm, y, "Stroj:")
    c.setFont(get_font(False), 11)
    c.drawString(left + 55 * mm, y, stroj or "-")
    y -= 8 * mm

    c.setFont(get_font(True), 11)
    c.drawString(left + 5 * mm, y, "Datum:")
    c.setFont(get_font(False), 11)
    c.drawString(left + 55 * mm, y, datum)
    y -= 12 * mm

    # Barcode
    barcode = make_barcode_code128(vyrobni)
    x = (w - barcode.width) / 2
    barcode.drawOn(c, x, y - 15 * mm)
    y -= 8 * mm

    c.setFont(get_font(True), 9)
    c.drawCentredString(center, y, f"Kód: {vyrobni}")

    c.save()
    return buffer


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
