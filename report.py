import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def send_report_email(report_text, subject="Solar Market Intel Report"):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    report_to = os.getenv("REPORT_TO")

    if not all([smtp_host, smtp_user, smtp_pass, report_to]):
        print("Email skipped: SMTP variables not set.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = report_to
    msg.attach(MIMEText(report_text, "plain"))

    with smtplib.SMTP(smtp_host, 587) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.sendmail(smtp_user, report_to, msg.as_string())
    print("Email sent to " + report_to)