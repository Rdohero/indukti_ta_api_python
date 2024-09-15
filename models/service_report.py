from initializers.mysql import db


class ServiceReport(db.Model):
    __tablename__ = 'service_reports'

    service_report_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    machine_name = db.Column(db.Text, nullable=False)
    complaints = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    status_id = db.Column(db.BigInteger, db.ForeignKey('statuses.status_id'), default=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), default=False)
    service_reports_items = db.relationship('ServiceReportItems',  lazy='joined', backref='service_reports')

    def __init__(self, date=None, image=None, name=None, machine_name=None, complaints=None, total_price=None,
                 date_end=None, status_id=None, user_id=None):
        self.date = date
        self.image = image
        self.name = name
        self.machine_name = machine_name
        self.complaints = complaints
        self.total_price = total_price
        self.date_end = date_end
        self.status_id = status_id
        self.user_id = user_id

    def to_dict(self, include_status=False, include_users=False, include_service_reports_items=False):
        return {
            'service_report_id': self.service_report_id,
            'date': self.date.strftime('%Y-%m-%dT%H:%M:%SZ') if self.date else None,
            'image': self.image,
            'name': self.name,
            'machine_name': self.machine_name,
            'complaints': self.complaints,
            'total_price': self.total_price,
            'date_end': self.date_end.strftime('%Y-%m-%dT%H:%M:%SZ') if self.date_end else None,
            'status_id': self.status_id,
            'user_id': self.user_id,
            'statuses': self.statuses.to_dict() if include_status and self.statuses else None,
            'users': self.users.to_dict() if include_users and self.users else None,
            'service_reports_items': [service_reports_items.to_dict(include_categories=True) for service_reports_items in
                                      self.service_reports_items] if include_service_reports_items else []
        }


class ServiceReportItems(db.Model):
    __tablename__ = 'service_reports_items'

    service_reports_items_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    store_items_id = db.Column(db.BigInteger, nullable=False)
    item_name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    category = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.category_id'), nullable=False)
    service_report_id = db.Column(db.BigInteger, db.ForeignKey('service_reports.service_report_id'), default=False)

    def __init__(self, store_items_id=None, item_name=None, quantity=None, price=None, category=None, category_id=None,
                 service_report_id=None):
        self.store_items_id = store_items_id
        self.item_name = item_name
        self.quantity = quantity
        self.price = price
        self.category = category
        self.category_id = category_id
        self.service_report_id = service_report_id

    def to_dict(self, include_categories=False, include_service_reports=False):
        return {
            'service_reports_items_id': self.service_reports_items_id,
            'store_items_id': self.store_items_id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'category_id': self.category_id,
            'service_report_id': self.service_report_id,
            'categories': self.categories.to_dict() if include_categories and self.categories else None,
            'service_reports': self.service_reports.to_dict() if include_service_reports and self.service_reports else None
        }
