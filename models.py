from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import Enum
db = SQLAlchemy()







class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    work_title = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('admin', 'staff', name='role_enum'), nullable=False, default='staff')
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Mapping of designate names to email addresses
DESIGNATE_EMAILS = {
    "Asha": "joelharold@ymail.com",
    "B.Ondero": "joelharold@ymail.com",
    "B. Odero": "ictsupport@pbora.go.ke",
    "Compliance": "ictsupport@pbora.go.ke",
    "D.O.S": "ictsupport@pbora.go.ke",
    "Eileen": "eileen@example.com",
    "Eric Njoroge": "eric.njoroge@example.com",
    "Esther": "esther@example.com",
    "Eznner": "eznner@example.com",
    "Finance": "finance@example.com",
    "Finance - Allan": "allan.finance@example.com",
    "Finance - Muktar": "muktar.finance@example.com",
    "Finance - Njane": "njane.finance@example.com",
    "Habiba": "habiba@example.com",
    "Investigations": "investigations@example.com",
    "Judy": "judy@example.com",
    "Kamande": "kamande@example.com",
    "Legal": "legal@example.com",
    "Legal - Vitalis": "vitalis.legal@example.com",
    "L.O - Cate": "cate.lo@example.com",
    "L.O. - Cate": "cate.lo2@example.com",
    "L.O. - Juliet": "juliet.lo@example.com",
    "L.O. - Lynn": "lynn.lo@example.com",
    "L.O. - Mercy": "mercy.lo@example.com",
    "L.O. - Michelle": "michelle.lo@example.com",
    "Naomi": "naomi@example.com",
    "N. Sankale": "nsankale@example.com",
    "Rukia": "rukia@example.com",
    "S.Monyoncho": "monyoncho@example.com",
    "Sarah": "sarah@example.com",
    "SDOR": "sdor@example.com",
    "Sankale": "sankale@example.com",
    "Topisia": "topisia@example.com"
}

# ...existing code...

DESIGNATE_WHATSAPP = {
    "Asha": "+254701446573",
    "B.Ondero": "+254701446573",
    "B. Odero": "+254701954150",
    "Compliance": "+254701954150",
    "D.O.S": "+254701954150",
    "Eileen": "+254701446573",
    "Eric Njoroge": "+254701446573",
    "Esther": "+254701446573",
    "Eznner": "+254701446573",
    "Finance": "+254701446573",
    "Finance - Allan": "+254701954150",
    "Finance - Muktar": "+254701954150",
    "Finance - Njane": "+254701954150",
    "Habiba": "+254700000013",
    "Investigations": "+254700000014",
    "Judy": "+254700000015",
    "Kamande": "+254700000016",
    "Legal": "+254700000017",
    "Legal - Vitalis": "+254700000018",
    "L.O - Cate": "+254700000019",
    "L.O. - Cate": "+254700000020",
    "L.O. - Juliet": "+254700000021",
    "L.O. - Lynn": "+254700000022",
    "L.O. - Mercy": "+254700000023",
    "L.O. - Michelle": "+254700000024",
    "Naomi": "+254700000025",
    "N. Sankale": "+254700000026",
    "Rukia": "+254700000027",
    "S.Monyoncho": "+254700000028",
    "Sarah": "+254729717332",
    "SDOR": "+254700000030",
    "Sankale": "+254700000031",
    "Topisia": "+254700000032"
}



DesignateEnum = Enum(
    "Asha",
    "B.Ondero",
    "B. Odero",
    "Compliance",
    "D.O.S",
    "Eileen",
    "Eric Njoroge",
    "Esther",
    "Eznner",
    "Finance",
    "Finance - Allan",
    "Finance - Muktar",
    "Finance - Njane",
    "Habiba",
    "Investigations",
    "Judy",
    "Kamande",
    "Legal",
    "Legal - Vitalis",
    "L.O - Cate",
    "L.O. - Cate",
    "L.O. - Juliet",
    "L.O. - Lynn",
    "L.O. - Mercy",
    "L.O. - Michelle",
    "Naomi",
    "N. Sankale",
    "Rukia",
    "S.Monyoncho",
    "Sarah",
    "SDOR",
    "Sankale",
    "Topisia",
    name="designate_enum"
)




class Dailytrackingregister(db.Model):
    __tablename__ = "dailytrackingregister"

    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.String(3000), nullable=False)
    service_requested = db.Column(db.String(3000), nullable=False)
    remarks = db.Column(db.Text)


class FileTracking(db.Model):
    __tablename__ = "filetracking"

    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.String(3000), nullable=True)
    service_requested = db.Column(db.String(3000), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    date_received = db.Column(db.Date, nullable=True)
    designate = db.Column(db.Enum(
        'Asha', 'B. Odero', 'D.O.S', 'Eileen', 'Eric Njoroge',
        'Esther', 'Eznner', 'Finance - Allan', 'Finance - Muktar', 'Finance - Njane',
        'Habiba', 'Judy', 'Kamande', 'Legal - Vitalis', 'L.O - Cate',
        'L.O. - Cate', 'L.O. - Juliet', 'L.O. - Lynn', 'L.O. - Mercy', 'L.O. - Michelle',
        'Naomi', 'N. Sankale', 'Rukia', 'S.Monyoncho', 'Sarah', 'SDOR', 'Sankale', 'Topisia',
        name='designate_enum'), nullable=True)
    filed_by_registry_action = db.Column(
        db.Enum('Filed', 'Not Filed', name='filed_status_enum'),
        nullable=True
    )

    date_filed = db.Column(db.Date, nullable=True)

    received_by_designate = db.Column(
        db.Enum('Received', 'Not Received', name='received_status_enum'),
        nullable=True
    )
    date_received_by_designate = db.Column(db.Date)
    correction_sent = db.Column(
        db.Enum('Correction Sent', 'No Correction Sent', name='correction_sent_enum'),
        nullable=True
    )
    date_correction_required = db.Column(db.Date, nullable=True)
    correction_status = db.Column(
        db.Enum('Correction Done', 'Correction Not Done', 'Not Required', name='correction_status_enum'),
        nullable=True
    )
    date_corrections_done = db.Column(db.Date)
    status = db.Column(db.Enum('Completed', 'Incomplete', name='status_enum'), nullable=True)
    date_completed = db.Column(db.Date, nullable=True)
    authorization = db.Column(db.Enum('Authorized', 'Unauthorized', name='authorization_enum'), nullable=True)
    date_authorised = db.Column(db.Date, nullable=True)
    signatory = db.Column(db.Enum('Monyoncho', 'I.Sang', name='signatory_enum'), nullable=True) ### Only these two accounts can dispatch after login
    dispatch = db.Column(db.Enum('Dispatched', 'Not Dispatched', name='dispatch_status'), default='Not Dispatched')
    date_dispatched = db.Column(db.Date)
