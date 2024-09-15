from initializers.mysql import db


class StoreItems(db.Model):
    __tablename__ = 'store_items'

    store_items_id = db.Column(db.BigInteger, primary_key=True)
    store_items_name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.category_id'), nullable=True)

    def __init__(self, store_items_name=None, quantity=None, price=None, category_id=None):
        self.store_items_name = store_items_name
        self.quantity = quantity
        self.price = price
        self.category_id = category_id

    def to_dict(self, include_categories=False):
        return {
            'store_items_id': self.store_items_id,
            'store_items_name': self.store_items_name,
            'quantity': self.quantity,
            'price': self.price,
            'categories': self.categories.to_dict() if include_categories and self.categories else None,
        }
