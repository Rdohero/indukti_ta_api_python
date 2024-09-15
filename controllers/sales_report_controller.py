from flask import Blueprint, request, jsonify
from initializers.mysql import db
from datetime import datetime, timedelta
from models.sales_report import SalesReports, SalesReportItems
from models.spare_part import SparePart
from models.store_item import StoreItems

sales_report_bp = Blueprint('sales_report_bp', __name__)


class Items:
    def __init__(self, id, item, price, category, category_items_id, quantity):
        self.id = id
        self.item = item
        self.price = price
        self.category = category
        self.category_items_id = category_items_id
        self.quantity = quantity


@sales_report_bp.route('/sales_report', methods=['POST'])
def sales_report():
    data = request.json
    sales_date = data.get('date')
    items_data = data.get('item', [])

    if not sales_date or not items_data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        sales_date = datetime.strptime(sales_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    total_price = sum(item['price'] * item['quantity'] for item in items_data)

    report = SalesReports(date=sales_date, total_price=total_price)

    try:
        db.session.add(report)
        db.session.commit()

        for item_data in items_data:
            category = item_data.get('category')
            item_id = item_data.get('id')
            quantity = item_data.get('quantity')

            if category == 'mesin':
                store_item = StoreItems.query.get(item_id)
                if not store_item or store_item.quantity < quantity:
                    db.session.rollback()
                    return jsonify({"error": f"Insufficient stock for item {item_id}"}), 400
                store_item.quantity -= quantity
                db.session.commit()
            elif category == 'spare_part':
                spare_part = SparePart.query.get(item_id)
                if not spare_part or spare_part.quantity < quantity:
                    db.session.rollback()
                    return jsonify({"error": f"Insufficient stock for spare part {item_id}"}), 400
                spare_part.quantity -= quantity
                db.session.commit()

            report_item = SalesReportItems(
                store_items_id=item_id,
                item_name=item_data['item'],
                quantity=quantity,
                price=item_data['price'],
                category=category,
                category_id=item_data['category_items_id'],
                sales_report_id=report.sales_report_id
            )
            db.session.add(report_item)
            db.session.commit()

        return jsonify({"success": "Sales report created successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@sales_report_bp.route('/sales_reports', methods=['GET'])
def get_sales_reports():
    sales_reports = SalesReports.query.order_by(SalesReports.date.desc()).all()
    return jsonify([sales_reports.to_dict(include_sales_report_items=True) for sales_reports in sales_reports]), 200


@sales_report_bp.route('/sales_reports/last_days', methods=['GET'])
def get_sales_reports_last_days():
    days = int(request.args.get('days', 0))
    months = int(request.args.get('months', 0))
    years = int(request.args.get('years', 0))

    adjusted_date = datetime.now() - timedelta(days=days) - timedelta(days=months * 30) - timedelta(days=years * 365)

    sales_reports = SalesReports.query.filter(SalesReports.date >= adjusted_date).order_by(
        SalesReports.date.desc()).all()
    return jsonify([report.to_dict() for report in sales_reports]), 200


@sales_report_bp.route('/sales_reports/date_range', methods=['GET'])
def get_sales_reports_by_date_range():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    sales_reports = SalesReports.query.filter(SalesReports.date.between(start_date, end_date)).order_by(
        SalesReports.date.desc()).all()
    return jsonify([report.to_dict() for report in sales_reports]), 200


@sales_report_bp.route('/sales_report/<int:id>', methods=['DELETE'])
def delete_sales_report(id):
    sales_report = SalesReports.query.get(id)
    if not sales_report:
        return jsonify({"error": "Sales report not found"}), 404

    try:
        SalesReportItems.query.filter_by(sales_report_id=id).delete()
        db.session.delete(sales_report)
        db.session.commit()
        return jsonify({"success": "Sales report deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@sales_report_bp.route('/sales_report/search', methods=['GET'])
def search_sales_report():
    order_id = request.args.get('order_id')
    sales_reports = SalesReports.query.filter_by(sales_report_id=order_id).all()

    if not sales_reports:
        return jsonify({"error": "Sales report not found"}), 404

    return jsonify([report.to_dict() for report in sales_reports]), 200
