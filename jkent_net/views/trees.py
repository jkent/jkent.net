from ..tree import Tree
from collections import OrderedDict
from flask import Blueprint, abort, current_app, redirect, render_template, request, session, send_file, url_for
import mimetypes
import os
import re

__all__ = ['bp']

bp = Blueprint('trees', __name__)

mimetypes.add_type('text/markdown', '.md')


def get_list(tree, path):
    if not tree.isdir(path):
        abort(404)

    try:
        paths = tree.list(path, recursive=True)
    except FileNotFoundError:
        abort(404)
    except PermissionError:
        abort(403)

    return {
        'version': tree.version,
        'paths': paths,
    }


@bp.route('/tree/<string:tree_id>/<path:tree_path>')
@bp.route('/tree/<string:tree_id>/')
@bp.route('/tree/<string:tree_id>')
def tree(tree_id, tree_path=''):
    session['version'] = request.args.get('version', session.get('version'))
    if request.args.get('version') != None:
        if session['version'] == '':
            session['version'] = None
        args = request.args.copy()
        del args['version']
        return redirect(url_for('trees.tree', tree_id=tree_id, tree_path=tree_path, **args))

    try:
        tree = Tree(current_app.repo, tree_id, session['version'])
    except FileNotFoundError:    
        abort(404)

    action = request.args.get('action')
    if action == 'list':
        return get_list(tree, tree_path)
    elif not (action == 'raw' or action == None):
        abort(501)

    if tree.isdir(tree_path):
        try:
            tree_path = tree.find_index(tree_path)
        except FileNotFoundError:
            abort(404)
        except PermissionError:
            abort(403)

    if action == 'raw':
        try:
            f = tree.open(tree_path, 'rb')
        except FileNotFoundError:
            abort(404)
        filename = os.path.basename(tree_path)
        return send_file(f, attachment_filename=filename)

    try:
        f = tree.open(tree_path, 'rb')
    except FileNotFoundError:
        abort(404)

    filename = os.path.basename(tree_path)
    mimetype = mimetypes.guess_type(filename) or 'application/octet-stream'
    return render_template('page.html')

@bp.route('/tree/<string:tree_id>/<path:tree_path>', methods=('POST',))
@bp.route('/tree/<string:tree_id>/', methods=('POST',))
@bp.route('/tree/<string:tree_id>', methods=('POST',))
def tree_post(tree_id, tree_path=''):
    tree_path = os.path.normpath(tree_path)
    tree = Tree(current_app.repo, tree_id, session.get('version'))