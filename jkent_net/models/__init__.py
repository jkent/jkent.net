from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy.types import TypeDecorator, VARCHAR


db = SQLAlchemy()


class JSONType(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


def init_app(app):
    db.init_app(app)

    @app.before_request
    def load_user():
        from flask import g, session

        g.user = None
        email = session.get('auth_email', None)

        if email is not None:
            g.user = User.query.filter_by(email=email).first()


from .user import *
from .document import *