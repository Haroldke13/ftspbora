from twilio.rest import Client
from config import Config
from models import DESIGNATE_WHATSAPP

# Mapping of designate names to SMS numbers (same as WhatsApp for now)
DESIGNATE_SMS = DESIGNATE_WHATSAPP


def send_sms_notification(designate_number, organization_name, service_requested):
    account_sid = Config.TWILIO_ACCOUNT_SID
    auth_token = Config.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message_body = f"New file for {organization_name} requesting {service_requested} has been assigned to you."
    message = client.messages.create(
        from_='+19842238887',
        body=message_body,
        to=designate_number
    )
    return message.sid
