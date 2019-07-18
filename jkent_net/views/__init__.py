from .login_github import *
from .pages import *
from flask import render_template
from flask_menu import Menu

menu = Menu()


def init_app(app):
    menu.init_app(app)
    app.register_blueprint(login_github.bp, url_prefix='/login')
    app.register_blueprint(pages.bp)

    @app.route('/')
    def index():
        return render_template('index.html')