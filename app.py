from flask import Flask, render_template, request, redirect, session, flash
import json, os, bcrypt, random, smtplib, time
import re 
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "sravya_super_secret_key"  # for session management

USER_DATA_FILE = "users.json"
OTP_STORE = {}


def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# Load user data
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

# Save user data
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

# Password Hashing
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP
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
        return True
    except Exception as e:
        print("Email send error:", e)
        return False

# Routes

@app.route("/")
def home():
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if not is_strong_password(password):
            flash("Password must be at least 8 characters long, include uppercase, lowercase, digit, and special character.", "error")
            return redirect("/signup")
        confirm = request.form["confirm"].strip()

        if password != confirm:
            flash("❌ Passwords do not match!", "error")
            return redirect("/signup")

        users = load_user_data()
        if username in users:
            flash("❌ Username already exists!", "error")
            return redirect("/signup")

        users[username] = {
            "password": hash_password(password),
            "fullname": fullname
        }

        save_user_data(users)
        flash("✅ Sign-up successful! Please login.", "success")
        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        users = load_user_data()

        if username not in users or not verify_password(password, users[username]):
            flash("Incorrect username or password!", "error")
            return redirect("/login")

        otp = generate_otp()
        OTP_STORE[username] = {
            "otp": otp,
            "timestamp": time.time(),
            "attempts": 0
        }
        session["username"] = username
        send_otp_email("sravyasrinivas13@gmail.com", otp)
        return redirect("/verify")

    return render_template("login.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    username = session.get("username")
    if not username or username not in OTP_STORE:
        return redirect("/login")

    if request.method == "POST":
        input_otp = request.form["otp"].strip()
        record = OTP_STORE.get(username)

        if time.time() - record["timestamp"] > 120:
            flash("OTP expired. Please login again.", "error")
            return redirect("/login")

        record["attempts"] += 1
        if record["attempts"] > 3:
            flash("Too many attempts. Try again.", "error")
            return redirect("/login")

        if input_otp == record["otp"]:
            OTP_STORE.pop(username)
            return redirect("/dashboard")
        else:
            flash(f"Incorrect OTP. Attempts left: {3 - record['attempts']}", "error")
            return redirect("/verify")

    return render_template("verify.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)