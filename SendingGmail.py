import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "phucanhnguyen17042006@gmail.com"

load_dotenv(override=True)
APP_PASSWORD = os.getenv('GOOGLE_APP_PASSWORD')

RECEIVER_EMAILS = ["phucanh17042000@gmail.com"]

SUBJECT = "Test Sending Gmail"
BODY = "Testing Successfully"


def send_email(subject, body, receiver_emails="phucanh17042000@gmail.com", sender_email="phucanhnguyen17042006@gmail.com"):
    # Tạo email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Kết nối đến SMTP server và gửi email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(sender_email, APP_PASSWORD)
        server.sendmail(sender_email, receiver_emails, msg.as_string())

    print("✅ Email đã được gửi thành công!")


# Test
if __name__ == "__main__":
    print(f"APP_PASSWORD: {APP_PASSWORD}")
    send_email(SUBJECT, BODY, RECEIVER_EMAILS)
