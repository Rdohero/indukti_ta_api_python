from flask import request, jsonify, Blueprint
from models.spare_part import SparePart
from models.store_item import StoreItems

search_bp = Blueprint('search_bp', __name__)


@search_bp.route('/search_machine', methods=['GET'])
def search_machine():
    categories_param = request.args.get('categories')
    name_param = request.args.get('name')

    query = StoreItems.query

    if categories_param:
        category_ids = [int(id) for id in categories_param.split(',')]
        query = query.filter(StoreItems.category_id.in_(category_ids))

    if name_param:
        query = query.filter(StoreItems.store_items_name.like(f"%{name_param}%"))

    store_items = query.all()

    return jsonify([store_items.to_dict(include_categories=True) for store_items in store_items]), 200


@search_bp.route('/search_spare_part', methods=['GET'])
def search_spare_part():
    categories_param = request.args.get('categories')
    name_param = request.args.get('name')

    query = SparePart.query

    if categories_param:
        category_ids = [int(id) for id in categories_param.split(',')]
        query = query.filter(SparePart.category_id.in_(category_ids))

    if name_param:
        query = query.filter(SparePart.spare_part_name.like(f"%{name_param}%"))

    spare_parts = query.all()

    return jsonify([spare_parts.to_dict(include_categories=True) for spare_parts in spare_parts]), 200
