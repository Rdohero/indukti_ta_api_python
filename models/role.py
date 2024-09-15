from initializers.mysql import db


class Role(db.Model):
    __tablename__ = 'roles'

    role_id = db.Column(db.BigInteger, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    users = db.relationship('User',  lazy='joined', backref='roles')

    def __init__(self, role_name=None):
        self.role_name = role_name

    def to_dict(self, include_users=False):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'users': [user.to_dict() for user in self.users] if include_users else []
        }

