from initializers.mysql import db
from models.spare_part import SparePart
from models.store_item import StoreItems


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.BigInteger, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)
    spare_parts = db.relationship('SparePart', lazy='joined', backref='categories')
    store_items = db.relationship('StoreItems', lazy='joined', backref='categories')
    sales_report_items = db.relationship('SalesReportItems', backref='categories')
    service_report_items = db.relationship('ServiceReportItems', backref='categories')

    def __init__(self, category_name=None):
        self.category_name = category_name

    def to_dict(self, include_spare_parts=False, include_store_items=False):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'spare_parts': [spare_part.to_dict() for spare_part in self.spare_parts] if include_spare_parts else [],
            'store_items': [store_item.to_dict() for store_item in self.store_items] if include_store_items else []
        }

