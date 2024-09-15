from initializers.mysql import db


class SparePart(db.Model):
    __tablename__ = 'spare_parts'

    spare_part_id = db.Column(db.BigInteger, primary_key=True)
    spare_part_name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.category_id'), nullable=True)

    def __init__(self, spare_part_name=None, quantity=None, price=None,category_id=None):
        self.spare_part_name = spare_part_name
        self.quantity = quantity
        self.price = price
        self.category_id = category_id

    def to_dict(self, include_categories=False):
        return {
            'spare_part_id': self.spare_part_id,
            'spare_part_name': self.spare_part_name,
            'quantity': self.quantity,
            'price': self.price,
            'categories': self.categories.to_dict() if include_categories and self.categories else None,
        }
