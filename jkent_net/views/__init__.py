from .admin import *
from .login_facebook import *
from .login_github import *
from .login_google import *
from .trees import *
from .users import *
from flask import render_template, session
from flask_login import user_logged_in, user_logged_out
from flask_menu import Menu
from flask_dance.contrib.github import github

menu = Menu()


def init_app(app):
    menu.init_app(app)
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(login_facebook.bp, url_prefix='/login')
    app.register_blueprint(login_github.bp, url_prefix='/login')
    app.register_blueprint(login_google.bp, url_prefix='/login')
    app.register_blueprint(trees.bp)
    app.register_blueprint(users.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @user_logged_in.connect_via(app)
    def _user_logged_in(sender, user, **extra):
        if 'avatar_url' not in session:
            user.init_avatar(user, None)

    @user_logged_out.connect_via(app)
    def _user_logged_out(sender, user, **extra):
        if 'avatar_url' in session:
            del session['avatar_url']
