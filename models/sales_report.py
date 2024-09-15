from initializers.mysql import db


class SalesReports(db.Model):
    __tablename__ = 'sales_reports'

    sales_report_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    total_price = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    sales_report_items = db.relationship('SalesReportItems',  lazy='joined', backref='sales_reports')

    def __init__(self, total_price=None, date=None):
        self.total_price = total_price
        self.date = date

    def to_dict(self, include_sales_report_items=False):
        return {
            'sales_report_id': self.sales_report_id,
            'total_price': self.total_price,
            'date': self.date.strftime('%Y-%m-%dT%H:%M:%SZ') if self.date else None,
            'sales_report_items': [sales_report_items.to_dict(include_categories=True) for sales_report_items in
                                   self.sales_report_items] if include_sales_report_items else []
        }


class SalesReportItems(db.Model):
    __tablename__ = 'sales_report_items'

    sales_report_items_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    store_items_id = db.Column(db.BigInteger, nullable=False)
    item_name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    category = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.category_id'), nullable=False)
    sales_report_id = db.Column(db.BigInteger, db.ForeignKey('sales_reports.sales_report_id'), default=False)

    def __init__(self, store_items_id=None, item_name=None, quantity=None, price=None, category=None, category_id=None,
                 sales_report_id=False):
        self.store_items_id = store_items_id
        self.item_name = item_name
        self.quantity = quantity
        self.price = price
        self.category = category
        self.category_id = category_id
        self.sales_report_id = sales_report_id

    def to_dict(self, include_categories=False, include_sales_reports=False):
        return {
            'sales_report_items_id': self.sales_report_items_id,
            'store_items_id': self.store_items_id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'category_id': self.category_id,
            'sales_report_id': self.sales_report_id,
            'categories': self.categories.to_dict() if include_categories and self.categories else None,
            'sales_reports': self.sales_report.to_dict() if include_sales_reports and self.sales_reports else None
        }
