from initializers.mysql import db
from models.role import Role
from models.service_report import ServiceReport


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    image = db.Column(db.Text, nullable=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.Text, nullable=True)
    no_handphone = db.Column(db.String, nullable=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey('roles.role_id'), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    service_reports = db.relationship('ServiceReport',  lazy='joined', backref='users')

    def __init__(self, image=None, username=None, password=None, address=None, no_handphone=None, role_id=None,
                 is_deleted=False):
        self.image = image
        self.username = username
        self.password = password
        self.address = address
        self.no_handphone = no_handphone
        self.role_id = role_id
        self.is_deleted = is_deleted

    def to_dict(self, include_role=False):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'address': self.address,
            'no_handphone': self.no_handphone,
            'role_id': self.role_id,
            'is_deleted': self.is_deleted,
            'roles': self.roles.to_dict() if include_role and self.roles else None
        }
