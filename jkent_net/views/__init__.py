from .auth import *
from flask_menu import Menu

menu = Menu()

def init_app(app):
    menu.init_app(app)
    app.register_blueprint(auth.bp)