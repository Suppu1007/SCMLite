from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

from app.core.config import EMAIL_SENDER, EMAIL_PASSWORD


# ============================================================
# GENERIC EMAIL SENDER (Base Function)
# ============================================================
def _send_email(to_email: str, subject: str, body: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("Email credentials missing — skipping email.")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email successfully sent to {to_email}")

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


# ============================================================
# ROLE CHANGE EMAIL
# ============================================================
def send_role_change_email(to_email: str, username: str, old_role: str, new_role: str, changed_by: str):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    subject = "SCMLite – Your Role Has Been Updated"

    body = f"""
Hello {username},

Your user role in SCMLite has been updated.

Old Role: {old_role}
New Role: {new_role}
Changed By: {changed_by}
Updated At: {timestamp}

If this change was not made by you, please contact SCMLite support immediately.

Regards,
SCMLite Admin Team
"""

    _send_email(to_email, subject, body)


# ============================================================
# SHIPMENT STATUS UPDATE EMAIL
# ============================================================
def send_shipment_status_email(
    to_email: str,
    shipment_id: str,
    sender_name: str,
    receiver_name: str,
    old_status: str,
    new_status: str,
    timestamp: str,
    iot_data: dict | None = None
):
    subject = f"SCMLite – Shipment {shipment_id} Status Updated"

    body = f"""
Shipment Update Notification

Shipment ID: {shipment_id}
Status Update: {old_status} → {new_status}
Updated At: {timestamp}

Sender: {sender_name}
Receiver: {receiver_name}
""".strip()

    # Optional IoT data
    if iot_data:
        body += "\n\nIoT Sensor Data:"
        if "Temperature" in iot_data:
            body += f"\n - Temperature: {iot_data['Temperature']}°C"
        if "Humidity" in iot_data:
            body += f"\n - Humidity: {iot_data['Humidity']}%"
        if "Battery_Level" in iot_data:
            body += f"\n - Battery Level: {iot_data['Battery_Level']}V"
        if "Route_From" in iot_data and "Route_To" in iot_data:
            body += f"\n - Current Route: {iot_data['Route_From']} → {iot_data['Route_To']}"
        if "Device_ID" in iot_data:
            body += f"\n - Device ID: {iot_data['Device_ID']}"

    body += "\n\nRegards,\nSCMLite Logistics System"

    _send_email(to_email, subject, body)


# ============================================================
# SEND EMAIL TO BOTH SENDER & RECEIVER
# ============================================================
def notify_shipment_status_change(shipment: dict, old_status: str, new_status: str, iot_data=None):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Sender
    if shipment.get("sender_email"):
        send_shipment_status_email(
            to_email=shipment["sender_email"],
            shipment_id=shipment["shipment_id"],
            sender_name=shipment["sender_name"],
            receiver_name=shipment["receiver_name"],
            old_status=old_status,
            new_status=new_status,
            timestamp=timestamp,
            iot_data=iot_data
        )

    # Receiver
    if shipment.get("receiver_email"):
        send_shipment_status_email(
            to_email=shipment["receiver_email"],
            shipment_id=shipment["shipment_id"],
            sender_name=shipment["sender_name"],
            receiver_name=shipment["receiver_name"],
            old_status=old_status,
            new_status=new_status,
            timestamp=timestamp,
            iot_data=iot_data
        )

    print(f"Shipment {shipment['shipment_id']} status emails sent to both parties.")
