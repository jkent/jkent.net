import os
from flask import Flask, g, render_template
from jkent_net.repository import Repository
from jkent_net.auth import login_required


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'jkent_net.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )
    app.config.from_pyfile('config.py', silent=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.repository_path = os.path.join(app.instance_path, 'repository')
    app.cache_path = os.path.join(app.instance_path, 'cache')

    app.repository = Repository(app.repository_path)

    import jkent_net.models
    models.init_app(app)

    import jkent_net.views
    views.init_app(app)

    import jkent_net.cli
    cli.init_app(app)

    return app