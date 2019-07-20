from ..models import db
from ..models.role import roles_users
import enum
import hashlib
from flask import session, url_for
from flask_security import AnonymousUser, UserMixin 
from urllib.parse import urlencode

__all__ = ['User', 'UserAvatarSource']


class UserAvatarSource(enum.Enum):
    disabled = 0
    auto = 1
    upload = 2
    oauth2 = 3
    gravitar = 4


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(2555), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    name = db.Column(db.Unicode(256))
    avatar_source = db.Column(db.Enum(UserAvatarSource),
                             default=UserAvatarSource.auto)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email

    def init_avatar(self, user, oauth2_url=None):
        url = url_for('static', filename='user.png', _external=True)
        if False and self.avatar_source in (UserAvatarSource.auto, UserAvatarSource.upload):
            pass # TODO: handle avatar uploads
        elif oauth2_url and self.avatar_source in (UserAvatarSource.auto, UserAvatarSource.oauth2):
            url = oauth2_url
        elif self.avatar_source in (UserAvatarSource.auto, UserAvatarSource.gravitar):
            hash = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
            url = 'https://www.gravatar.com/avatar/{}?{}'.format(hash, urlencode({'d': url, 's': 64}))
        session['avatar_url'] = url

    def any_role(self, *roles):
        return any(x in roles for x in self.roles)

    def all_roles(self, *roles):
        return all(x in roles for x in self.roles)

AnonymousUser.any_role = lambda self, *roles: False
AnonymousUser.all_roles = lambda self, *roles: False