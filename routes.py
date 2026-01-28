

from flask import session
from models import User
from decorators import login_required, admin_required
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Dailytrackingregister, FileTracking
from sendsms import send_sms_notification, DESIGNATE_SMS

routes = Blueprint("routes", __name__)


# DELETE FILE ROUTE
@routes.route('/delete-file/<int:file_id>', methods=['POST'])
@admin_required
def delete_file(file_id):
    file = FileTracking.query.get_or_404(file_id)
    designate = file.designate
    org_name = file.organization_name
    service_requested = file.service_requested
    db.session.delete(file)
    db.session.commit()
    # Notify designate via email
    from models import DESIGNATE_EMAILS
    from flask_mail import Message
    from app import mail
    email_sent = False
    if designate and designate in DESIGNATE_EMAILS:
        recipient = DESIGNATE_EMAILS[designate]
        try:
            msg = Message(
                subject=f"File Deleted: {org_name}",
                recipients=[recipient],
                body=f"The file for organization {org_name} has been deleted from the system."
            )
            mail.send(msg)
            email_sent = True
        except Exception as e:
            flash(f"Error sending email to {designate}: {str(e)}", "danger")
    # WhatsApp notification
    from config import send_whatsapp_notification
    from models import DESIGNATE_WHATSAPP
    if designate and designate in DESIGNATE_WHATSAPP:
        designate_number = f"whatsapp:{DESIGNATE_WHATSAPP[designate]}"
        try:
            send_whatsapp_notification(designate_number, org_name, f"DELETED the file for service : {service_requested}")
            flash(f"WhatsApp message sent to {designate} ({designate_number})!", "success")
        except Exception as e:
            flash(f"WhatsApp message failed: {str(e)}", "danger")
    flash('Record deleted successfully.', 'success')
    return redirect(url_for('routes.records'))


# SIGNUP ROUTE
@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('routes.profile'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        work_title = request.form['work_title']
        role = request.form['role']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')
        user = User(name=name, email=email, department=department, work_title=work_title, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('signup.html')

# LOGIN ROUTE
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('routes.profile'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('routes.profile'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# LOGOUT ROUTE
@routes.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('routes.login'))

# PROFILE ROUTE
@routes.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@routes.route("/add-row", methods=["POST"])
def add_row():
    from datetime import datetime
    def parse_date(val):
        try:
            return datetime.strptime(val, "%Y-%m-%d").date() if val else None
        except Exception:
            return None

    file = FileTracking(
        organization_name=request.form.get("organization_name"),
        service_requested=request.form.get("service_requested"),
        remarks=request.form.get("remarks"),
        date_received=parse_date(request.form.get("date_received")),
        date_correction_required=parse_date(request.form.get("date_correction_required")),
        designate=request.form.get("designate") or None,
        filed_by_registry_action=request.form.get("filed_by_registry_action") or None,
        date_filed=parse_date(request.form.get("date_filed")),
        received_by_designate=request.form.get("received_by_designate") or None,
        date_received_by_designate=parse_date(request.form.get("date_received_by_designate")),
        correction_sent=request.form.get("correction_sent") or None,
        # 'sent_by' removed (not in canonical CSV)
        correction_status=request.form.get("correction_status") or None,
        date_corrections_done=parse_date(request.form.get("date_corrections_done")),
        status=request.form.get("status") or None,
        date_completed=parse_date(request.form.get("date_completed")),
        authorization=request.form.get("authorization") or None,
        date_authorised=parse_date(request.form.get("date_authorised")),
        signatory=request.form.get("signatory") or None,
        dispatch=request.form.get("dispatch") or None,
        date_dispatched=parse_date(request.form.get("date_dispatched"))
    )

    # Only admin can add
    if 'role' not in session or session.get('role') != 'admin':
        flash('Only admin can add records.', 'danger')
        return redirect(url_for('routes.records'))
    db.session.add(file)
    db.session.commit()

    # Email notification logic
    from models import DESIGNATE_EMAILS
    from flask_mail import Message
    from app import mail
    designate = file.designate
    email_sent = False
    if designate and designate in DESIGNATE_EMAILS:
        recipient = DESIGNATE_EMAILS[designate]
        try:
            msg = Message(
                subject=f"New File Assigned to {designate}",
                recipients=[recipient],
                body=f"A new file has been assigned to you as designate: {designate}. Please log in to view details."
            )
            mail.send(msg)
            email_sent = True
        except Exception as e:
            flash(f"Error sending email to {designate}: {str(e)}", "danger")
    if email_sent:
        flash(f"Email sent to {designate}", "success")
    flash('New record added!', 'success')
    return redirect(url_for('routes.records'))



@routes.route("/edit-enum/<int:file_id>", methods=["POST"])
def edit_enum(file_id):
    file = FileTracking.query.get_or_404(file_id)
    # List of enum fields and their possible values
    enum_fields = {
        'designate': ['Asha','B. Odero','D.O.S','Eileen','Eric Njoroge','Esther','Eznner','Finance - Allan','Finance - Muktar','Finance - Njane','Habiba','Judy','Kamande','Legal - Vitalis','L.O - Cate','L.O. - Cate','L.O. - Juliet','L.O. - Lynn','L.O. - Mercy','L.O. - Michelle','Naomi','N. Sankale','Rukia','S.Monyoncho','Sarah','SDOR','Sankale','Topisia'],
        'filed_by_registry_action': ['Filed','Not Filed'],
        'received_by_designate': ['Received','Not Received'],
        'correction_sent': ['Correction Sent','No Correction Sent'],
        'correction_status': ['Correction Done','Correction Not Done','Not Required'],
        'status': ['Completed','Incomplete'],
        'authorization': ['Authorized','Unauthorized'],
        'signatory': ['Monyoncho','I.Sang'],
        'dispatch': ['Dispatched','Not Dispatched']
    }
    # --- Notification tracking ---
    tracked_fields = [
        'filed_by_registry_action', 'date_filed', 'received_by_designate', 'date_received_by_designate',
        'correction_sent', 'date_correction_required', 'correction_status',
        'date_corrections_done', 'status', 'date_completed', 'authorization', 'date_authorised',
        'signatory', 'dispatch', 'date_dispatched'
    ]
    old_values = {field: getattr(file, field) for field in tracked_fields}

    changed_fields = []
    # Update enum fields
    # sent_by and staff_sent_correction_email removed (not present in canonical CSV)

    for field, options in enum_fields.items():
        val = request.form.get(field)
        if val in options or val == '':
            old_val = getattr(file, field)
            if val == '':
                if old_val is not None:
                    changed_fields.append(field)
                setattr(file, field, None)
            else:
                if old_val != val:
                    changed_fields.append(field)
                setattr(file, field, val)

    date_fields = [
        'date_received', 'date_filed', 'date_received_by_designate', 'date_correction_required', 'date_corrections_done',
        'date_completed', 'date_authorised', 'date_dispatched'
    ]
    from datetime import datetime
    for field in date_fields:
        val = request.form.get(field)
        old_val = getattr(file, field)
        if val:
            try:
                new_val = datetime.strptime(val, "%Y-%m-%d").date()
                if old_val != new_val:
                    changed_fields.append(field)
                setattr(file, field, new_val)
            except Exception:
                pass
        elif val == '':
            if old_val is not None:
                changed_fields.append(field)
            setattr(file, field, None)

    if changed_fields:
        # Only admin can edit
        if 'role' not in session or session.get('role') != 'admin':
            flash('Only admin can edit records.', 'danger')
            return redirect(url_for('routes.records'))
        db.session.commit()
        # Email notification logic
        from models import DESIGNATE_EMAILS
        from flask_mail import Message
        from app import mail
        designate = file.designate
        email_sent = False
        if designate and designate in DESIGNATE_EMAILS:
            recipient = DESIGNATE_EMAILS[designate]
            try:
                # Compose a detailed message about what changed
                changes = []
                for field in changed_fields:
                    before = old_values.get(field)
                    after = getattr(file, field)
                    changes.append(f"{field.replace('_', ' ').title()}: {before} → {after}")
                change_msg = "\n".join(changes)
                msg = Message(
                    subject=f"File Update Notification for {designate}",
                    recipients=[recipient],
                    body=f"A file for {file.organization_name} has been updated. The following fields changed:\n\n{change_msg}\n\nPlease log in to view details."
                )
                mail.send(msg)
                email_sent = True
            except Exception as e:
                flash(f"Error sending email to {designate}: {str(e)}", "danger")
        if email_sent:
            flash(f"Email sent to {designate}", "success")
        # WhatsApp notification logic (after commit, for designate changes)
        from config import send_whatsapp_notification
        from models import DESIGNATE_WHATSAPP
        designate = file.designate
        if designate and designate in DESIGNATE_WHATSAPP:
            designate_number = f"whatsapp:{DESIGNATE_WHATSAPP[designate]}"
            try:
                # WhatsApp message with changes
                changes = []
                for field in changed_fields:
                    before = old_values.get(field)
                    after = getattr(file, field)
                    changes.append(f"{field.replace('_', ' ').title()}: {before} → {after}")
                change_msg = ", ".join(changes)
                send_whatsapp_notification(designate_number, file.organization_name, f"Updated fields: {change_msg}")
                flash(f"WhatsApp message sent to {designate} ({designate_number})!", "danger")
            except Exception as e:
                flash(f"WhatsApp message failed: {str(e)}", "danger")
        flash('Record updated!', 'success')
    else:
        flash('No changes made.', 'info')
    return redirect(url_for('routes.records'))
# Edit enum columns for FileTracking

# Place this after routes = Blueprint(...)



# 1️⃣ INDEX – Preliminary File Tracking
@routes.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        record = Dailytrackingregister(
            organization_name=request.form["organization_name"],
            service_requested=request.form["service_requested"],
            remarks=request.form["remarks"]
        )
        db.session.add(record)
        db.session.commit()

        return redirect(url_for("routes.register", record_id=record.id))

    return render_template("index.html")


# 2️⃣ MAIN FILE TRACKING ROUTE
@routes.route("/register/<int:record_id>", methods=["GET", "POST"])
def register(record_id):
    prelim = Dailytrackingregister.query.get_or_404(record_id)



    if request.method == "POST":
        file = FileTracking(
            organization_name=request.form.get("organization_name", prelim.organization_name),
            service_requested=request.form.get("service_requested", prelim.service_requested),
            remarks=request.form.get("remarks", prelim.remarks),
            date_received=request.form.get("date_received") or None,
            date_correction_required=request.form.get("date_correction_required") or None,
            designate=request.form.get("designate"),
            filed_by_registry_action=request.form.get("filed_by_registry_action"),
            received_by_designate=request.form.get("received_by_designate"),
            date_received_by_designate=request.form.get("date_received_by_designate") or None,
            correction_sent=request.form.get("correction_sent"),
            correction_status=request.form.get("correction_status"),
            date_corrections_done=request.form.get("date_corrections_done") or None,
            status=request.form.get("status"),
            date_completed=request.form.get("date_completed") or None,
            authorization=request.form.get("authorization"),
            date_authorised=request.form.get("date_authorised") or None,
            signatory=request.form.get("signatory"),
            dispatch=request.form.get("dispatch"),
            date_dispatched=request.form.get("date_dispatched") or None
        )
        
        db.session.add(file)
        db.session.commit()
        # Email notification logic
        from models import DESIGNATE_EMAILS
        from flask_mail import Message
        from app import mail
        # SMS notification logic
        from sendsms import send_sms_notification, DESIGNATE_SMS
        if designate and designate in DESIGNATE_SMS:
            sms_number = DESIGNATE_SMS[designate]
            try:
                send_sms_notification(sms_number, file.organization_name, file.service_requested)
                flash(f"SMS sent to {designate} ({sms_number})!", "success")
            except Exception as e:
                flash(f"SMS failed: {str(e)}", "danger")
        designate = file.designate
        email_sent = False
        if designate and designate in DESIGNATE_EMAILS:
            recipient = DESIGNATE_EMAILS[designate]
            
            try:
                msg = Message(
                    subject=f"New File Assigned to {designate}",
                    recipients=[recipient],
                    body=f"A new file has been assigned to you as designate: {designate}. Please log in to view details."
                )
                mail.send(msg)
                email_sent = True
            except Exception as e:
                flash(f"Error sending email to {designate}: {str(e)}", "danger")
        if email_sent:
            flash(f"Email sent to {designate}", "success")

        # WhatsApp notification logic
        from config import send_whatsapp_notification
        from models import DESIGNATE_WHATSAPP
        designate_number = None
        if file.designate and file.designate in DESIGNATE_WHATSAPP:
            designate_number = f"whatsapp:{DESIGNATE_WHATSAPP[file.designate]}"
            try:
                send_whatsapp_notification(designate_number, file.organization_name, file.service_requested)
                flash(f"WhatsApp message sent to {file.designate} ({designate_number})!", "success")
            except Exception as e:
                flash(f"WhatsApp message failed: {str(e)}", "danger")

        return redirect(url_for("routes.records"))

    return render_template("register.html", prelim=prelim)


# 3️⃣ DISPLAY RECORDS

@routes.route("/records")
def records():
    search = request.args.get('search', '').strip()
    column = request.args.get('column', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'desc')
    query = FileTracking.query
    if search:
        # Define column types
        string_columns = [
            'organization_name', 'service_requested', 'remarks'
        ]
        enum_columns = [
            'designate', 'filed_by_registry_action', 'received_by_designate', 'correction_sent',
            'correction_status', 'status', 'authorization', 'signatory', 'dispatch'
        ]
        bool_columns = []
        date_columns = [
                'date_received', 'date_received_by_designate', 'date_correction_required', 'date_corrections_done',
            'date_completed', 'date_authorised', 'date_dispatched'
        ]
        int_columns = ['id']

        if column and hasattr(FileTracking, column):
            if column in string_columns:
                query = query.filter(getattr(FileTracking, column).ilike(f"%{search}%"))
            elif column in enum_columns:
                query = query.filter(getattr(FileTracking, column).cast(db.String).ilike(f"%{search}%"))
            elif column in bool_columns:
                if search.lower() in ['true', 'yes', '1']:
                    query = query.filter(getattr(FileTracking, column) == True)
                elif search.lower() in ['false', 'no', '0']:
                    query = query.filter(getattr(FileTracking, column) == False)
            elif column in int_columns:
                if search.isdigit():
                    query = query.filter(getattr(FileTracking, column) == int(search))
            elif column in date_columns:
                query = query.filter(getattr(FileTracking, column).cast(db.String).ilike(f"%{search}%"))
        else:
            # Search all columns (OR logic)
            filters = []
            for col in string_columns:
                if hasattr(FileTracking, col):
                    filters.append(getattr(FileTracking, col).ilike(f"%{search}%"))
            for col in enum_columns:
                if hasattr(FileTracking, col):
                    filters.append(getattr(FileTracking, col).cast(db.String).ilike(f"%{search}%"))
            for col in bool_columns:
                if hasattr(FileTracking, col):
                    if search.lower() in ['true', 'yes', '1']:
                        filters.append(getattr(FileTracking, col) == True)
                    elif search.lower() in ['false', 'no', '0']:
                        filters.append(getattr(FileTracking, col) == False)
            for col in int_columns:
                if hasattr(FileTracking, col) and search.isdigit():
                    filters.append(getattr(FileTracking, col) == int(search))
            for col in date_columns:
                if hasattr(FileTracking, col):
                    filters.append(getattr(FileTracking, col).cast(db.String).ilike(f"%{search}%"))
            if filters:
                query = query.filter(db.or_(*filters))
    # Sorting logic
    valid_sort_columns = [
        'id', 'organization_name', 'service_requested', 'remarks', 'date_received', 'designate',
        'filed_by_registry_action', 'received_by_designate', 'date_received_by_designate',
        'correction_sent', 'date_correction_required', 'correction_status', 'date_corrections_done', 'status',
        'date_completed', 'authorization', 'date_authorised', 'signatory', 'dispatch', 'date_dispatched'
    ]
    if sort_by in valid_sort_columns:
        sort_col = getattr(FileTracking, sort_by)
        if sort_order == 'asc':
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(FileTracking.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    files = pagination.items
    return render_template("records.html", files=files, pagination=pagination, page=page, per_page=per_page, search=search, column=column, sort_by=sort_by, sort_order=sort_order)



@routes.route('/test-email')
def test_email():
    from flask_mail import Message
    from app import mail
    msg = Message(subject="Test Email", recipients=["joelharold@ymail.com"], body="This is a test.")
    try:
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return f"Error: {e}"

@routes.route("/test-whatsapp")
def test_whatsapp():
    from config import send_whatsapp_notification
    from models import DESIGNATE_WHATSAPP
    designate = "Asha"
    organization_name = "Test Organization"
    service_requested = "Test Service"
    designate_number = f"whatsapp:{DESIGNATE_WHATSAPP[designate]}"
    try:
        send_whatsapp_notification(designate_number, organization_name, service_requested)
        flash(f"WhatsApp message sent to {designate} ({designate_number})!", "success")
    except Exception as e:
        flash(f"WhatsApp message failed: {str(e)}", "danger")
    return redirect(url_for("routes.records"))

@routes.route("/test-sms")
def test_sms():
                from sendsms import send_sms_notification, DESIGNATE_SMS
                designate = "Asha"
                sms_number = DESIGNATE_SMS[designate]
                try:
                    sid = send_sms_notification(sms_number, "TestOrg", "TestService")
                    return f"SMS sent to {designate} ({sms_number})! SID: {sid}", 201
                except Exception as e:
                    return f"SMS failed: {str(e)}", 500