from .repository import Repository
from .ext.security import ExtendedRegisterForm
from flask import Flask, g, render_template
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore
import os

mail = Mail()


def create_app():
    global security, user_datastore

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if os.environ.get('FLASK_ENV') == 'development':
        app.config['SECRET_KEY'] = 'development'
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'jkent_net.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )
    app.config.from_pyfile('config.py', silent=True)

    app.repository_path = os.path.join(app.instance_path, 'repository')
    app.repository = Repository(app.repository_path)

    app.cache_root = os.path.join(app.instance_path, 'cache')

    from . import models
    models.init_app(app)

    mail.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(models.db, models.User, models.Role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

    from . import views
    views.init_app(app)

    from . import cli
    cli.init_app(app)

    return app