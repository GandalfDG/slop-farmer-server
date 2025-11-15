"""Send emails for account verification through Resend API"""
from slopserver.settings import settings
import resend

resend.api_key = settings.resend_token

def send_email(to: str, subject, content):
    params: resend.Emails.SendParams = {
        "from": "slopfarmer@jack-case.pro",
        "to": to,
        "subject": subject,
        "html": content
    }

    email: resend.Emails.SendResponse = resend.Emails.send(params)

    return email

def generate_verification_email(verification_url: str):
    return f"""
    <p>click here to verify your Slop Farmer account: <a href={verification_url}>{verification_url}</a></p>
    """