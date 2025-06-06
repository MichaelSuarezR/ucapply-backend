from flask import Flask, request, jsonify
import smtplib
import ssl
import random
import os

app = Flask(__name__)

# In-memory store for email → code
from datetime import datetime, timedelta

CODES_DB = {}  # email → (code, timestamp)

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "No email provided"}), 400

    code = str(random.randint(100000, 999999))
    CODES_DB[email] = (code, datetime.utcnow())

    try:
        send_verification_email(email, code)
        return jsonify({"message": f"Verification code sent to {email}"}), 200
    except Exception as e:
        print("❌ Email error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    saved = CODES_DB.get(email)
    if not saved:
        return jsonify({"success": False, "error": "No code found"}), 400

    saved_code, saved_time = saved
    if datetime.utcnow() - saved_time > timedelta(minutes=2):
        return jsonify({"success": False, "error": "Code expired"}), 400

    if str(saved_code) != str(code):
        return jsonify({"success": False, "error": "Incorrect code"}), 400

    print("⏳ Stored:", CODES_DB)
    print("📩 Received:", email, code)

    return jsonify({"success": True})

def send_verification_email(to_email, code):
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    
    if not sender or not password:
        raise Exception("Missing sender email or password environment variable")

    subject = "Your UCApply Verification Code"
    body = f"Your UCApply verification code is: {code}"
    msg = f"Subject: {subject}\n\n{body}"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg)

RESET_CODES = {}  # email → (code, timestamp)

@app.route("/send-reset-code", methods=["POST"])
def send_reset_code():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "No email provided"}), 400

    code = str(random.randint(100000, 999999))
    RESET_CODES[email] = (code, datetime.utcnow())

    try:
        send_verification_email(email, code)
        return jsonify({"message": f"Reset code sent to {email}"}), 200
    except Exception as e:
        print("❌ Reset email error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("newPassword")

    if not all([email, code, new_password]):
        return jsonify({"success": False, "error": "Missing fields"}), 400

    saved = RESET_CODES.get(email)
    if not saved:
        return jsonify({"success": False, "error": "No reset code found"}), 400

    saved_code, saved_time = saved
    if datetime.utcnow() - saved_time > timedelta(minutes=5):
        return jsonify({"success": False, "error": "Reset code expired"}), 400

    if str(saved_code) != str(code):
        return jsonify({"success": False, "error": "Incorrect code"}), 400

    try:
        # Replace with actual user account update logic if persistent storage
        print(f"🔐 Password for {email} would be updated to: {new_password}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/internships", methods=["GET"])
def internships():
    try:
        city = request.args.get("city", "")
        response = requests.get("https://www.arbeitnow.com/api/job-board-api")
        jobs = response.json().get("data", [])

        # Filter jobs with 'intern' or 'internship' in title
        filtered = [
            {
                "title": job["title"],
                "company": job["company_name"],
                "location": job.get("location", ""),
                "url": job.get("url", "")
            }
            for job in jobs
            if "intern" in job["title"].lower() or "internship" in job["title"].lower()
        ]

        print(f"✅ Returning {len(filtered)} internships")
        return jsonify(filtered)

    except Exception as e:
        print("❌ Backend error:", e)
        return jsonify({"error": str(e)}), 500

def is_english(text):
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

filtered = [
    {
        "title": job["title"],
        "company": job["company_name"],
        "location": job.get("location", ""),
        "url": job.get("url", "")
    }
    for job in jobs
    if ("intern" in job["title"].lower() or "internship" in job["title"].lower())
    and is_english(job["title"])
]

if __name__ == "__main__":
    app.run(debug=True)
