from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps


def required_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_identity = get_jwt_identity()
            request.user_id = user_identity
        except:
            return jsonify({"error": "Token tidak valid atau sudah kadaluarsa"}), 401

        return f(*args, **kwargs)

    return decorated_function
