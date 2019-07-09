import os
from flask import Flask, g, render_template
from flask_menu import register_menu
from flask_breadcrumbs import register_breadcrumb
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
    @register_breadcrumb(app, '.', 'Home')
    def index():
        return render_template('index.html')

    @app.route('/projects')
    @register_menu(app, '.projects', 'Projects')
    @register_breadcrumb(app, '.projects', 'Projects')
    def projects():
        return render_template('index.html')

    @app.route('/projects/pybot')
    @register_menu(app, '.projects.pybot', 'Pybot')
    @register_breadcrumb(app, '.projects.pybot', 'Pybot')
    def pybot():
        return render_template('index.html')

    @app.route('/projects/pybot/modules')
    @register_menu(app, '.projects.pybot.modules', 'Modules')
    @register_breadcrumb(app, '.projects.pybot.modules', 'Modules')
    def modules():
        return render_template('index.html')

    @app.route('/contact')
    @register_menu(app, '.contact', 'Contact')
    @register_breadcrumb(app, '.contact', 'Contact')
    def contact():
        return render_template('index.html')

    import jkent_net.cli
    cli.init_app(app)

    return app
