from flask import request, jsonify, Blueprint
from werkzeug.security import generate_password_hash
import random
import jwt
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import threading

from initializers.mysql import db
from models.user import User

otp_store = {}
lock = threading.Lock()


def simpan_otp(otp_str, token):
    with lock:
        otp_store[otp_str] = token


def dapatkan_otp_string(otp_str):
    with lock:
        if otp_str not in otp_store:
            return None
        return otp_store[otp_str]


def hapus_otp(otp_str):
    with lock:
        if otp_str in otp_store:
            del otp_store[otp_str]


otp_bp = Blueprint('otp_bp', __name__)


@otp_bp.route('/resend_otp', methods=['POST'])
def resend_otp_email_pass_ver():
    data = request.json
    username = data.get('username')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"Error": "User not found"}), 404

    otp = random.randint(100000, 999999)
    otp_str = f"{otp:06d}"

    token = jwt.encode({
        "username": username,
        "otp": otp,
        "exp": (datetime.now() + timedelta(minutes=1)).timestamp()
    }, os.getenv("SECRET"), algorithm="HS256")

    simpan_otp(otp_str, token)

    subject = "Email Verification"
    html_body = f"""
        <html>
            <h1>Code to Verify Email For User : {username}</h1>
            <p>{otp_str}</p>
        </html>
    """

    send_email("athillahaidar@gmail.com", subject, html_body)
    send_email("rojaridho8888@gmail.com", subject, html_body)

    return jsonify({"Status": "Send Code Success"}), 200


def send_email(to_email, subject, html_body):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = MIMEText(html_body, "html")
    msg['Subject'] = subject
    msg['From'] = f"Mojopahit <{sender_email}>"
    msg['To'] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


@otp_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    otp = data.get('otp')

    token = dapatkan_otp_string(otp)
    if not token:
        return jsonify({"Error": "Invalid OTP"}), 400

    try:
        decoded_token = jwt.decode(token, os.getenv("SECRET"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        hapus_otp(otp)
        return jsonify({"Error": "OTP has expired"}), 401

    if decoded_token['username'] != username or str(decoded_token['otp']) != otp:
        return jsonify({"Error": "OTP not valid"}), 401

    # Update password
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"Error": "User not found"}), 404

    hashed_password = generate_password_hash(password)
    user.password = hashed_password
    db.session.commit()

    hapus_otp(otp)

    return jsonify({"Status": "Success"}), 200
