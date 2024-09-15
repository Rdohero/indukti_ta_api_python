from flask import Blueprint, request, jsonify
from models.spare_part import SparePart
from initializers.mysql import db

spare_part_bp = Blueprint('spare_part_bp', __name__)


@spare_part_bp.route('/spare_part', methods=['GET'])
def get_spare_parts():
    spare_parts = SparePart.query.all()
    return jsonify({
        "success": "Success getting spare parts",
        "data": [spare_part.to_dict(include_categories=True) for spare_part in spare_parts]
    }), 200


@spare_part_bp.route('/spare_part', methods=['POST'])
def create_spare_part():
    data = request.json
    spare_part_name = data.get('spare_part_name')
    quantity = data.get('quantity')
    price = data.get('price')
    category_id = data.get('category_id')

    spare_part = SparePart(
        spare_part_name=spare_part_name,
        quantity=quantity,
        price=price,
        category_id=category_id
    )

    try:
        db.session.add(spare_part)
        db.session.commit()

        spare_parts = SparePart.query.all()
        return jsonify({
            "success": "Spare part created successfully",
            "data": [spare_part.to_dict(include_categories=True) for spare_part in spare_parts]
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@spare_part_bp.route('/preorder_spare_part', methods=['POST'])
def pre_order_spare_part():
    data = request.json
    spare_part_id = data.get('spare_part_id')
    quantity = data.get('quantity')
    price = data.get('price')

    spare_part = SparePart.query.filter_by(spare_part_id=spare_part_id).first()

    if not spare_part:
        return jsonify({"error": "Spare part not found"}), 404

    try:
        if price != 0 and price != spare_part.price:
            new_price = price * quantity
            old_price = spare_part.price * spare_part.quantity
            total_quantity = spare_part.quantity + quantity
            spare_part.price = (new_price + old_price) / total_quantity
        spare_part.quantity += quantity

        db.session.commit()
        return jsonify({"success": "Spare part pre-order successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@spare_part_bp.route('/edit_spare_part', methods=['PUT'])
def edit_spare_part():
    data = request.json
    spare_part_id = data.get('spare_part_id')
    spare_part_name = data.get('spare_part_name')
    quantity = data.get('quantity')
    price = data.get('price')
    category_id = data.get('category_id')

    spare_part = SparePart.query.filter_by(spare_part_id=spare_part_id).first()

    if not spare_part:
        return jsonify({"error": "Spare part not found"}), 404

    try:
        if spare_part_name and spare_part_name != spare_part.spare_part_name:
            spare_part.spare_part_name = spare_part_name
        if quantity is not None and quantity != spare_part.quantity:
            spare_part.quantity = quantity
        if price is not None and price != spare_part.price:
            spare_part.price = price
        if category_id is not None and category_id != spare_part.category_id:
            spare_part.category_id = category_id

        db.session.commit()
        return jsonify({"success": "Spare part updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@spare_part_bp.route('/delete_spare_part/<int:id>', methods=['DELETE'])
def delete_spare_part(id):
    spare_part = SparePart.query.filter_by(spare_part_id=id).first()

    if not spare_part:
        return jsonify({"error": "Spare part not found"}), 404

    try:
        db.session.delete(spare_part)
        db.session.commit()
        return jsonify({"success": "Spare part deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
