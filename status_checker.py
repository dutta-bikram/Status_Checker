import requests
import os
import smtplib
from email.mime.text import MIMEText

STATUS_FILE = "status.txt"

# Load previous status from file
def load_previous_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()
    return ""

# Save current status to file
def save_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)

# Get current status from website
def check_status(applid):
    url = f"https://castcertificatewb.gov.in/applsearch?applid={applid}"
    response = requests.get(url)
    data = response.json()

    if data["recordsTotal"] == 1:
        return data["data"][0]["status_desc"]
    else:
        return "No record"

# Send email notification
def send_email(new_status, applid):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not sender or not password or not receiver:
        print("❌ Missing email credentials in environment.")
        return

    subject = "🔔 Caste Certificate Status Changed"
    body = f"The new status for application {applid} is:\n\n{new_status}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Failed to send email:", e)

# Main logic
def main():
    applid = os.getenv("APPL_ID")
    if not applid:
        print("❌ Environment variable 'APPL_ID' is not set.")
        return

    prev_status = load_previous_status()
    new_status = check_status(applid)

    if new_status != prev_status:
        print(f"🔔 Status changed! New status: {new_status}")
        send_email(new_status, applid)
        save_status(new_status)
    else:
        print(f"No change. Current status: {new_status}")

if __name__ == "__main__":
    main()
