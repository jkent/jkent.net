from ..tree import Tree
from collections import OrderedDict
from flask import Blueprint, abort, current_app, redirect, render_template, request, session, send_file, url_for
import mimetypes
import os
import re
import shutil
from werkzeug.utils import secure_filename

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
    try:
        tree = Tree(current_app.repo, tree_id, session['version'])
    except FileNotFoundError:    
        abort(404)

    action = request.args.get('action')
    if action == 'upload':
        dest = re.sub('^/|\.\./', '', request.form['dest'])
        for file in request.files.getlist('files'):
            path = secure_filename(file.filename)
            path = os.path.join(tree.repo.path, tree.path, dest, filename)
            file.save(path)
        return get_list(tree, dest)
    elif action == 'copy' or action == 'move':
        dest = re.sub('^/|\.\./', '', request.form['dest'])
        for path in request.form.getlist('paths'):
            path = re.sub('^/|\.\./', '', path)
            src_path = os.path.join(tree.repo.path, tree.path, path)
            dst_path = os.path.join(tree.repo.path, tree.path, dest)
            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
                if action == 'move':
                    os.remove(src_path)
                continue
            if path.endswith('/') or path == '':
                dst_path = os.path.join(dst_path, os.path.basename(path[:-1]))
                print('dst_path', dst_path)
            for src_dir, _, files in os.walk(src_path):
                dst_dir = src_dir.replace(src_path, dst_path)
                if not os.path.exists(dst_dir):
                    os.mkdir(dst_dir)
                for file in files:
                    shutil.copy(os.path.join(src_dir, file),
                        os.path.join(dst_dir, file))
                if action == 'move':
                    shutil.rmtree(src_path)
        return get_list(tree, dest)