import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
import os

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", 
                  (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    # Fetch credentials from environment
    sender_email = os.environ.get("SMTP_EMAIL", "").strip()
    sender_password = os.environ.get("SMTP_PASSWORD", "").strip()
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    
    # We print the OTP for testing/simulation purposes
    print(f"\n{'='*40}")
    print(f"🔐 SIMULATED EMAIL TO {receiver_email}")
    print(f"🔐 YOUR OTP IS: {otp}")
    print(f"{'='*40}\n")
    
    # Placeholders often found in .env.example or template files
    placeholders = ["your_email@gmail.com", "your_app_password", "YOUR_EMAIL", "YOUR_PASSWORD", ""]
    
    is_placeholder = sender_email in placeholders or sender_password in placeholders
    
    if is_placeholder:
        print("💡 SMTP credentials not configured correctly (using placeholders). Falling back to console simulation.")
        return True # Simulate success in dev mode
        
    try:
        msg = MIMEText(f"Your Smart Campus Energy Optimization System OTP is: {otp}")
        msg['Subject'] = 'Login OTP - Smart Campus'
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error sending real email via SMTP: {e}")
        print("💡 Make sure your SMTP credentials are correct or use placeholders for console-only testing.")
        return False
