from ..models import db
from ..models.role import roles_users
import enum
from flask_security import UserMixin

__all__ = ['User', 'UserImageSource']


class UserImageSource(enum.Enum):
    disabled = 0
    auto = 1
    oauth2 = 2
    gravitar = 3
    upload = 4


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(2555), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    name = db.Column(db.Unicode(256))
    image_source = db.Column(db.Enum(UserImageSource),
                             default=UserImageSource.auto)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


    def __repr__(self):
        return '<User %r>' % self.email