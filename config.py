import os
from twilio.rest import Client

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///dailytracking_db.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "super-secret-key"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'juellharold@gmail.com'
    MAIL_PASSWORD = 'jegfsboukvpibium'
    MAIL_DEFAULT_SENDER = 'juellharold@gmail.com'

    # Google OAuth configuration
    GOOGLE_CLIENT_ID = '1052110297217-3pi3l4eqhktgocn2cjrvt03bqurvu2qq.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'
    GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

    TWILIO_ACCOUNT_SID = 'AC59522a6761edae997ba183dddf47dbd4'
    TWILIO_AUTH_TOKEN = 'ae64f69c38e80d5f83b0ec73f7fd1596'
    TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

def send_whatsapp_notification(designate_number, organization_name, service_requested):
    account_sid = Config.TWILIO_ACCOUNT_SID
    auth_token = Config.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message_body = f"New file for {organization_name} requesting {service_requested} has been assigned to you."
    message = client.messages.create(
        from_=Config.TWILIO_WHATSAPP_NUMBER,
        body=message_body,
        to=designate_number
    )
    return message.sid