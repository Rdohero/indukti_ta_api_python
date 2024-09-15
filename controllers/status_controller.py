from flask import Blueprint, jsonify
from models.status import Status

status_bp = Blueprint('status_bp', __name__)


@status_bp.route('/status', methods=['GET'])
def get_all_status():
    statues = Status.query.all()

    if statues:
        return jsonify([statues.to_dict(include_service_reports=True) for statues in statues])
    else:
        return jsonify({"error": "Status not found"}), 404
