import smtplib
import random
from dotenv import load_dotenv
load_dotenv()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")

    subject = "Your OTP Verification Code"
    body = f"Hello,\n\nYour OTP code is: {otp}\nIt will expire in 2 minutes.\n\nThank you!"

    email_text = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, email_text)
        print("OTP sent successfully to", to_email)
        return True
    except Exception as e:
        print("Failed to send OTP:", e)
        return False
