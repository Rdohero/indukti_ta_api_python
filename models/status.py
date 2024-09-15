from initializers.mysql import db


class Status(db.Model):
    __tablename__ = 'statuses'

    status_id = db.Column(db.BigInteger, primary_key=True)
    status_name = db.Column(db.Text(50), nullable=False)
    service_reports = db.relationship('ServiceReport',  lazy='joined', backref='statuses')

    def to_dict(self, include_service_reports=False):
        return {
            'status_id': self.status_id,
            'status_name': self.status_name,
            'service_reports': [service_report.to_dict() for service_report in self.service_reports] if
            include_service_reports else []
        }

