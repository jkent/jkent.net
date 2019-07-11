from .auth import *
from .pages import *
from .posts import *
from flask_menu import Menu

menu = Menu()

def init_app(app):
    menu.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(posts.bp)