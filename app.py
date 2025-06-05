from flask import Flask, request, jsonify
import smtplib
import ssl
import random
import os

app = Flask(__name__)

# In-memory store for email → code
VERIFICATION_CODES = {}

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "No email provided"}), 400

    code = str(random.randint(100000, 999999))
    VERIFICATION_CODES[email] = code

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
        return jsonify({"success": False, "error": "Email and code required"}), 400

    expected_code = VERIFICATION_CODES.get(email)

    if expected_code == code:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Invalid verification code"}), 400

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
