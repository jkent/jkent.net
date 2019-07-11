import enum
from jkent_net.models import db

__all__ = ['User']


class ImageSource(enum.Enum):
    none = 0
    gravitar = 1
    upload = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(256), nullable=False, unique=True)
    hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.Unicode(256), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False)
    image_source = db.Column(db.Enum(ImageSource), nullable=False, default=ImageSource.none)
    documents = db.relationship('Document', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.email
