from flask import Blueprint, jsonify
from models.role import Role

role_bp = Blueprint('role_bp', __name__)


@role_bp.route('/role', methods=['GET'])
def get_all_user():
    roles = Role.query.all()

    if roles:
        return jsonify([role.to_dict(include_users=True) for role in roles])
    else:
        return jsonify({"error": "Role not found"}), 404
