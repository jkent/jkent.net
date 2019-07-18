import enum
from jkent_net.models import db

__all__ = ['User', 'UserImageSource']


class UserImageSource(enum.Enum):
    disabled = 0
    auto = 1
    oauth2 = 2
    gravitar = 3
    upload = 4


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(256), nullable=False, unique=True)
    hash = db.Column(db.String(128), nullable=True)
    name = db.Column(db.Unicode(256), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False)
    image_source = db.Column(db.Enum(UserImageSource), nullable=False, default=UserImageSource.auto)
    #subtrees = db.relationship('Subtree', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.email
