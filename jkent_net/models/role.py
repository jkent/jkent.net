from ..models import db
from flask_security import RoleMixin
import json

__all__ = ['Role', 'RoleCollection']

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class RoleCollection(list):
    @property
    def json(self):
        return json.dumps([role.name for role in self])