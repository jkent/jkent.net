from .auth import *
from flask_breadcrumbs import Breadcrumbs

breadcrumbs = Breadcrumbs()

def init_app(app):
    breadcrumbs.init_app(app)
    app.register_blueprint(auth.bp)