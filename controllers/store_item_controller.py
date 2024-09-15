from flask import Blueprint, request, jsonify
from initializers.mysql import db
from models.store_item import StoreItems

store_item_bp = Blueprint('store_items_bp', __name__)


@store_item_bp.route('/store_items', methods=['GET'])
def get_store_items():
    store_items = StoreItems.query.all()
    return jsonify({
        "success": "Success getting store items",
        "data": [store_items.to_dict(include_categories=True) for store_items in store_items]
    }), 200


@store_item_bp.route('/preorder_store_items', methods=['POST'])
def pre_order_store_items():
    data = request.json
    store_items_id = data.get('store_items_id')
    quantity = data.get('quantity')
    price = data.get('price')

    store_item = StoreItems.query.filter_by(store_items_id=store_items_id).first()

    if not store_item:
        return jsonify({"error": "Store item not found"}), 404

    try:
        if price != 0 and price != store_item.price:
            new_price = price * quantity
            old_price = store_item.price * store_item.quantity
            total_quantity = store_item.quantity + quantity
            store_item.price = (new_price + old_price) / total_quantity
        store_item.quantity += quantity

        db.session.commit()
        return jsonify({"success": "Store items pre-order successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@store_item_bp.route('/store_item', methods=['POST'])
def create_store_item():
    data = request.json
    store_items_name = data.get('store_items_name')
    quantity = data.get('quantity')
    price = data.get('price')
    category_id = data.get('category_id')

    store_item = StoreItems(
        store_items_name=store_items_name,
        quantity=quantity,
        price=price,
        category_id=category_id
    )

    try:
        db.session.add(store_item)
        db.session.commit()

        store = StoreItems.query.all()
        return jsonify({
            "success": "Store item created successfully",
            "data": [store_items.to_dict(include_categories=True) for store_items in store]
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@store_item_bp.route('/edit_store_item', methods=['PUT'])
def edit_store_item():
    data = request.json
    store_items_id = data.get('store_items_id')
    store_items_name = data.get('store_items_name')
    quantity = data.get('quantity')
    price = data.get('price')
    category_id = data.get('category_id')

    store_item = StoreItems.query.filter_by(store_items_id=store_items_id).first()

    if not store_item:
        return jsonify({"error": "Store item not found"}), 404

    try:
        if store_items_name and store_items_name != store_item.store_items_name:
            store_item.store_items_name = store_items_name
        if quantity is not None and quantity != store_item.quantity:
            store_item.quantity = quantity
        if price is not None and price != store_item.price:
            store_item.price = price
        if category_id is not None and category_id != store_item.category_id:
            store_item.category_id = category_id

        db.session.commit()
        return jsonify({"success": "Store item updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@store_item_bp.route('/delete_store_item/<int:id>', methods=['DELETE'])
def delete_store_item(id):
    store_item = StoreItems.query.filter_by(store_items_id=id).first()

    if not store_item:
        return jsonify({"error": "Store item not found"}), 404

    try:
        db.session.delete(store_item)
        db.session.commit()
        return jsonify({"success": "Store item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
