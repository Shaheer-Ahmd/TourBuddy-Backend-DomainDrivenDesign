import os
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage

EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EVENT_ID = "366"
SMS_SENDER_FROM = "Tour Buddy"


def send_email(subject: str, text: str, to: str):
    
    # Create a secure SSL context
    em = EmailMessage()

    em["Subject"] = subject
    em["From"] = EMAIL_FROM
    em["To"] = to
    em.set_content(text)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, to, em.as_string())
