from ..models import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

__all__ = ['OAuth']


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')