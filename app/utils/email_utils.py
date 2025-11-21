from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

from app.core.config import EMAIL_SENDER, EMAIL_PASSWORD


def send_role_change_email(to_email: str, old_role: str, new_role: str, changed_by: str):
    """
    Sends an email notification when a user's role is changed.
    """

    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("Email credentials missing. Skipping email.")
        return

    subject = "SCMLite – Role Update Notification"

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    body = f"""
Hi {username},

Your SCMLite role has been changed to: {new_role}.

If you didn’t request this change, please contact SCMLite support immediately.

Regards,
SCMLite Admin Team

""".strip()

    try:
        # Create email container
        message = MIMEMultipart()
        message["From"] = EMAIL_SENDER
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # SMTP Server Login
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        # Send email
        server.send_message(message)
        server.quit()

        print(f"Role update email sent to {to_email}")

    except Exception as e:
        print(f"Failed to send role update email to {to_email}: {e}")
