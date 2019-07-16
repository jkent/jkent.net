from .auth import *
from .pages import *
from .subtree import *
from flask import render_template
from flask_menu import Menu

menu = Menu()


def init_app(app):
    menu.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(subtree.bp)

    @app.route('/')
    def index():
        return render_template('index.html')