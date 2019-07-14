from ..auth import admin_required
from ..subtree import Subtree
from flask import Blueprint, Response, abort, current_app, g, redirect, render_template, request, send_file, url_for
import io
from jinja2 import Markup
import magic
import re

__all__ = ['bp']

bp = Blueprint('subtree', __name__)


@bp.route('/s/<string:id>/')
@bp.route('/s/<string:id>/<path:path>')
def subtree(id, path=''):
    s = Subtree(current_app.repository, current_app.cache_root, id)

    version = request.args.get('v')

    if request.path.endswith('/') and s.file_exists(path, version):
        data = b'\n'.join(s.list(path, version))
        return Response(data, mimetype='text/plain')

    file, mimetype = s.read(path, version)
    if file == None:
        abort(404)

    return send_file(file, mimetype=mimetype)