import os
from flask import Flask, g, render_template
from flask_menu import register_menu
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

    import jkent_net.models
    models.init_app(app)

    import jkent_net.views
    views.init_app(app)

    @app.route('/')
    @register_menu(app, '.', 'Home')
    def index():
        return render_template('index.html')

    @app.route('/about')
    @register_menu(app, '.about', 'About')
    def about():
        return render_template('about.html')

    @app.route('/connect')
    @register_menu(app, '.connect', 'Connect')
    def contact():
        return render_template('connect.html')

    import jkent_net.cli
    cli.init_app(app)

    return app
