import json
import bcrypt
import time
import random
import smtplib
import os

USER_DATA_FILE = "users.json"

# Load user data from file
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as file:
        return json.load(file)

# Save user data to file
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

# Hash password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Check password
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# OTP generation
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via Gmail
def send_otp_email(to_email, otp):
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = "your_app_password_here"

    subject = "Your OTP Verification Code"
    body = f"Hello,\n\nYour OTP code is: {otp}\nIt will expire in 2 minutes.\n\nThank you!"
    email_text = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, email_text)
        print("✅ OTP sent successfully to", to_email)
        return True
    except Exception as e:
        print("❌ Failed to send OTP:", e)
        return False

# Sign-up
def sign_up(username, password):
    user_data = load_user_data()
    if username in user_data:
        return "Username already exists! Please choose a different one."
    hashed_pw = hash_password(password)
    user_data[username] = hashed_pw
    save_user_data(user_data)
    return "✅ Sign-up successful! You can now log in."

# Login + OTP
def check_login(username, password):
    user_data = load_user_data()
    if username not in user_data:
        return "Username not found!"

    if not verify_password(password, user_data[username]):
        return "❌ Incorrect password!"

    print("✅ Login successful! Proceed to OTP verification.")
    otp = generate_otp()
    email_sent = send_otp_email(sender_email, otp)

    if email_sent:
        start_time = time.time()
        max_attempts = 3
        attempts = 0
        verified = False

        while attempts < max_attempts:
            if time.time() - start_time > 120:
                print("⏰ OTP expired. Please login again.")
                break

            input_otp = input("Enter the OTP sent to your email: ").strip()
            attempts += 1

            if input_otp == otp:
                print("✅ OTP verified! Access granted.")
                verified = True
                break
            else:
                print(f"❌ Incorrect OTP. Attempts left: {max_attempts - attempts}")
        
        if not verified:
            print("🚫 Too many incorrect attempts. Access denied.")
    return None

# Main Program
def main():
    while True:
        print("\n🔐 Welcome to Secure Login System")
        print("1. Sign Up")
        print("2. Login")
        print("0. Exit")
        try:
            choice = int(input("Enter your choice: ").strip())
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == 1:
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            print(sign_up(username, password))

        elif choice == 2:
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            result = check_login(username, password)
            if result:
                print(result)

        elif choice == 0:
            print("👋 Goodbye!")
            break
        else:
            print("Invalid option. Try again.")