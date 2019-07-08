from os import getenv
from werkzeug.debug import DebuggedApplication
from jkent_net import create_app

app = create_app()

flask_env = getenv('FLASK_ENV', 'production')
if flask_env == 'development':
    app = DebuggedApplication(app, evalex=True)