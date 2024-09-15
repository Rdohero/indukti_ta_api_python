from flask import Blueprint, jsonify, request

from initializers.mysql import db
from models.category import Category

category_bp = Blueprint('category_bp', __name__)


@category_bp.route('/category', methods=['GET'])
def get_all_category():
    categories = Category.query.all()

    if categories:
        return jsonify([categories.to_dict(include_spare_parts=True, include_store_items=True) for categories
                        in categories])
    else:
        return jsonify({"error": "Role not found"}), 404


@category_bp.route('/category', methods=['POST'])
def create_category():
    category_name = request.json.get('category_name')

    if not category_name:
        return jsonify({"error": "Category name is required"}), 400

    try:
        new_category = Category(category_name=category_name)

        db.session.add(new_category)
        db.session.commit()

        categories = Category.query.all()

        if categories:
            return jsonify({
                "success": "Successfully created category",
                "data": [categories.to_dict(include_spare_parts=True, include_store_items=True) for categories
                         in categories]
            }), 200
        else:
            return jsonify({"error": "Category not found"}), 404
    except Exception as e:
        db.session.rollback()
        return (jsonify({"error": str(e)}),
                400)


@category_bp.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)

    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Successfully deleted category."}), 200
    else:
        return jsonify({"error": "Category not found or already deleted."}), 404


@category_bp.route('/category', methods=['PUT'])
def edit_category():
    data = request.json

    category_id = data.get('category_id')
    category_name = data.get('category_name')

    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    if category_name and category_name != category.category_name:
        category.category_name = category_name

    try:
        db.session.commit()
        return jsonify({"success": "Category updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update Category"}), 500
