import os
import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.utils import secure_filename
from initializers.mysql import mysql, db
from middleware.auth import required_auth
from models.user import User

user_bp = Blueprint('user_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user:
        stored_hashed_password = user.password.encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            access_token = create_access_token(identity=user.user_id)
            return jsonify(access_token=access_token)
        else:
            return jsonify({"error": "Invalid password"}), 401
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@user_bp.route('/login/owner', methods=['POST'])
def login_owner():
    body = request.json
    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = User.query.filter_by(username=username, is_deleted=False).first()

    if not user:
        return jsonify({"error": "Username or password is incorrect"}), 400

    if user.role_id != 1:
        return jsonify({"error": "Not an owner account"}), 400
    stored_hashed_password = user.password.encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        return jsonify({"error": "Username or password is incorrect"}), 400

    token = create_access_token(identity=user.user_id)

    return jsonify({"token": token}), 200


@user_bp.route('/getuser', methods=['GET'])
@required_auth
def get_user():
    user_id = request.user_id
    user = User.query.get(user_id)

    if user:
        return jsonify(user.to_dict(include_role=True))
    else:
        return jsonify({"error": "User not found"}), 404


@user_bp.route('/user', methods=['GET'])
def get_all_user():
    users = User.query.filter_by(is_deleted=False).all()

    if users:
        return jsonify([user.to_dict() for user in users])
    else:
        return jsonify({"error": "User not found"}), 404


@user_bp.route('/register', methods=['POST'])
def register():
    image = request.files['image']
    username = request.form['username']
    password = request.form['password']
    address = request.form['address']
    NoHandphone = request.form['no_handphone']
    role = request.form['role']

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=14))

    if image and allowed_file(image.filename):
        isDataHere = User.query.filter_by(username=username, is_deleted=True).first()
        if isDataHere:
            filepath = None
            if image:
                os.remove(isDataHere.image)
                filename = secure_filename(image.filename)
                filepath = os.path.join("images/", filename)
                os.makedirs("images", exist_ok=True)
                image.save(filepath)

            try:
                User.query.filter_by(username=username).update({
                    "password": hashed_password,
                    "address": address,
                    "no_handphone": NoHandphone,
                    "image": filepath if image else isDataHere.image,
                    "role_id": role,
                    "is_deleted": False
                })
                db.session.commit()
                return jsonify({"message": "User added successfully!"})

            except Exception as e:
                db.session.rollback()
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"error": "Failed to add user"}), 400
        else:
            filename = secure_filename(image.filename)

            filepath = os.path.join("images/", filename)

            image.save(filepath)

            user = User(username=username, password=hashed_password, role_id=role, address=address,
                        no_handphone=NoHandphone
                        , image=filepath if image else None)

            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"error": "Failed to add user"}), 400
            return jsonify({"message": "User added successfully!"})
    else:
        return jsonify({"error": "Invalid file type or no file uploaded!"}), 400


@user_bp.route('/user-detail', methods=['GET'])
def get_user_by_id():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    users = User.query.get(user_id)

    if users:
        return jsonify(users.to_dict(include_role=True))
    else:
        return jsonify({"error": "User not found"}), 404


@user_bp.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id, is_deleted=False).first()

    if user:
        try:
            user.is_deleted = True
            db.session.commit()
            return jsonify({"message": "User Successfully deleted"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to delete user."}), 400
    else:
        return jsonify({"error": "User not found or already deleted."}), 404
