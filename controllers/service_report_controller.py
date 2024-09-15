from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from initializers.mysql import db
from models.service_report import ServiceReport, ServiceReportItems
from models.spare_part import SparePart
from models.store_item import StoreItems

service_report_bp = Blueprint('service_report_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    name, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{name}_{timestamp}{ext}"


@service_report_bp.route('/service_report', methods=['POST'])
def create_service_report():
    try:
        date = request.form.get('date')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        machine_name = request.form.get('machine_name')
        complaints = request.form.get('complaints')

        if 'image' not in request.files:
            return jsonify({"error": "Image file missing"}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join('images', unique_filename)
            file.save(file_path)
        else:
            return jsonify({"error": "Allowed image types are jpg, jpeg, png, svg"}), 400

        try:
            parsed_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        service_report = ServiceReport(
            date=parsed_date,
            date_end=None,
            image=file_path,
            name=name,
            machine_name=machine_name,
            complaints=complaints,
            status_id=1,
            user_id=user_id
        )

        db.session.add(service_report)
        db.session.commit()

        service_reports = ServiceReport.query.order_by(ServiceReport.date.desc()).all()
        return jsonify({"success": "Service report created", "data": [service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@service_report_bp.route('/edit_service_report', methods=['PUT'])
def edit_service_report():
    data = request.get_json()
    try:
        service_id = data.get('service_id')
        complaints = data.get('complaints')
        total_price = data.get('total_price')
        items = data.get('item', [])

        service_report = ServiceReport.query.filter_by(service_report_id=service_id).first()

        if not service_report:
            return jsonify({"error": "Service report not found"}), 404

        if complaints:
            service_report.complaints = complaints
        if total_price:
            service_report.total_price = total_price

        if items:
            for item in items:
                if item['category'] == 'mesin':
                    store_item = StoreItems.query.filter_by(store_items_id=item['id']).first()
                    if store_item and store_item.quantity >= item['quantity']:
                        store_item.quantity -= item['quantity']
                        db.session.add(store_item)
                    else:
                        return jsonify({"error": f"Insufficient stock for item {item['item']}"}), 400
                elif item['category'] == 'spare_part':
                    spare_part = SparePart.query.filter_by(spare_part_id=item['id']).first()
                    if spare_part and spare_part.quantity >= item['quantity']:
                        spare_part.quantity -= item['quantity']
                        db.session.add(spare_part)
                    else:
                        return jsonify({"error": f"Insufficient stock for spare part {item['item']}"}), 400

                service_report_item = ServiceReportItems(
                    store_items_id=item['id'],
                    item_name=item['item'],
                    quantity=item['quantity'],
                    price=item['price'],
                    category=item['category'],
                    category_id=item['category_items_id'],
                    service_report_id=service_report.service_report_id
                )
                db.session.add(service_report_item)

        service_report.status_id = 2
        service_report.date_end = datetime.datetime.now()

        db.session.commit()

        return jsonify({"success": "Service report updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@service_report_bp.route('/service_reports', methods=['GET'])
def get_service_reports():
    try:
        service_reports = ServiceReport.query.order_by(ServiceReport.date.desc()).all()
        return jsonify({"success": "Service reports fetched", "data": [service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@service_report_bp.route('/service_reports/status/<int:id>', methods=['GET'])
def get_service_report_by_status_id(id):
    service_reports = ServiceReport.query.filter_by(status_id=id) \
        .order_by(ServiceReport.date.desc(), ServiceReport.service_report_id.desc()) \
        .all()

    return jsonify({
        "Success": "Success Getting Service Report",
        "Data": [service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]
    }), 200


@service_report_bp.route('/service_reports/user/<int:id>', methods=['GET'])
def get_service_report_by_user_id(id):
    service_reports = ServiceReport.query.filter_by(user_id=id, status_id=1) \
        .order_by(ServiceReport.date.asc(), ServiceReport.service_report_id.asc()) \
        .all()

    return jsonify({
        "Success": "Success Getting Service Report",
        "Data": [service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]
    }), 200


@service_report_bp.route('/service_reports/last_days', methods=['GET'])
def get_service_reports_last_days():
    days = request.args.get('days', default=0, type=int)
    months = request.args.get('months', default=0, type=int)
    years = request.args.get('years', default=0, type=int)

    adjusted_date = datetime.now() - timedelta(days=days) - timedelta(days=months * 30) - timedelta(days=years * 365)

    service_reports = ServiceReport.query.filter(ServiceReport.date >= adjusted_date,
                                                 ServiceReport.status_id == 2).order_by(ServiceReport.date.desc(),
                                                                                        ServiceReport.service_report_id.
                                                                                        desc()).all()

    return jsonify([service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]), 200


@service_report_bp.route('/service_reports/date_range', methods=['GET'])
def get_service_reports_by_date_range():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    service_reports = ServiceReport.query.filter(ServiceReport.date.between(start_date, end_date),
                                                 ServiceReport.status_id == 2).order_by(ServiceReport.date.desc(),
                                                                                        ServiceReport.service_report_id.
                                                                                        desc()).all()

    return jsonify([service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]), 200


@service_report_bp.route('/service_reports/search', methods=['GET'])
def search_service():
    order_id = request.args.get('order_id')

    service_reports = ServiceReport.query.filter_by(service_report_id=order_id) \
        .all()

    if len(service_reports) == 0:
        return jsonify({"error": "Service Tidak Ditemukan"}), 404

    return jsonify([service_reports.to_dict(
            include_service_reports_items=True, include_users=True, include_status=True) for service_reports in
            service_reports]), 200
