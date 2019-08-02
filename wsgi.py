from os import getenv
from werkzeug.debug import DebuggedApplication
from jkent_net import create_app

app = create_app()

flask_env = getenv('FLASK_ENV', 'production')
if flask_env == 'development':
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    app = DebuggedApplication(app, evalex=True)
