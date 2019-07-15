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
    raw = request.args.get('raw')
    history = request.args.get('history')

    if history:
        history = s.history(path, version)
        return Response(repr(history), mimetype='text/plain')

    if not s.file_exists(path, version):
        abort(404)

    if s.isdir(path, version):
        index = s.find_index(path, version)
        if not index:
            data = b'\n'.join(s.list(path, version))
            return Response(data, mimetype='text/plain')
        path = index

    file, mimetype = s.read(path, version, raw)
    if file == None:
        abort(404)

    return send_file(file, mimetype=mimetype)