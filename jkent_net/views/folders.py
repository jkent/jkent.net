from ..folder import Folder
from collections import OrderedDict
from ..converter import convert_to_html
from flask import Blueprint, abort, current_app, redirect, render_template, request, session, send_file, url_for
import mimetypes
import os
import re
import shutil
from werkzeug.utils import secure_filename

__all__ = ['bp']

bp = Blueprint('folder', __name__)

mimetypes.add_type('text/markdown', '.md')


@bp.route('/folder/<string:folder_id>/<path:folder_path>')
@bp.route('/folder/<string:folder_id>/')
@bp.route('/folder/<string:folder_id>')
def folder(folder_id, folder_path=''):
    session['version'] = request.args.get('version', session.get('version'))
    if request.args.get('version') != None:
        if session['version'] == '':
            session['version'] = None
        args = request.args.copy()
        del args['version']
        return redirect(url_for('folder.folder', folder_id=folder_id, folder_path=folder_path, **args))

    try:
        folder = Folder(current_app.repo, folder_id, session['version'])
    except FileNotFoundError:    
        abort(404)

    action = request.args.get('action')
    if action not in ['browse', 'list']:
        if folder.isdir(folder_path):
            try:
                folder_path = folder.find_index(folder_path)
            except FileNotFoundError:
                abort(404)
            except PermissionError:
                abort(403)

    if action == 'list':
        try:
            paths = folder.list('', recursive=True)
        except FileNotFoundError:
            abort(404)
        except PermissionError:
            abort(403)

        return {
            'version': folder.version,
            'paths': paths,
        }
    elif action in [None, 'edit', 'raw']:
        try:
            f = folder.open(folder_path, 'rb')
        except FileNotFoundError:
            abort(404)
        except PermissionError:
            abort(403)

        if action == None:
            pass

        filename = os.path.basename(folder_path)
        mime, _ = mimetypes.guess_type(filename)

        if action == 'edit':
            if not mime or not mime.startswith('text/'):
                abort(501)
        elif action == 'raw':
            return send_file(f, attachment_filename=filename)
        elif mime and mime.startswith('image/'):
            return render_template('preview.html', **{
                'page': {
                    'action': action,
                    'base': url_for('folder.folder', folder_id=folder_id),
                    'mime': mime,
                    'type': 'folder',
                    'version': folder.version,
                },
                'folder': {
                    'path': folder_path,
                },
            })
        elif mime and mime.startswith('text/'):
            f, fragment = convert_to_html(f, mime)
            if not fragment:
                return send_file(f, attachment_filename=filename)
            return render_template('page.html', **{
                'page': {
                    'action': action,
                    'base': url_for('folder.folder', folder_id=folder_id),
                    'content': f.read().decode('utf8'),
                    'mime': mime,
                    'type': 'folder',
                    'version': folder.version,
                },
                'folder': {
                    'path': folder_path,
                },
            })
        else: 
            return send_file(f, attachment_filename=filename)

    elif action == 'browse':
        return render_template('folder.html', **{
            'page': {
                'action': action,
                'base': url_for('folder.folder', folder_id=folder_id),
                'type': 'folder',
                'version': folder.version
            },
            'folder': {
                'path': folder_path,
            },
        })
    else:
        abort(501)


@bp.route('/folder/<string:folder_id>/<path:folder_path>', methods=('POST',))
@bp.route('/folder/<string:folder_id>/', methods=('POST',))
@bp.route('/folder/<string:folder_id>', methods=('POST',))
def folder_post(folder_id, folder_path=''):
    try:
        folder = Folder(current_app.repo, folder_id, session['version'])
    except FileNotFoundError:    
        abort(404)

    action = request.args.get('action')
    if action == 'upload':
        dest = re.sub('^/|\.\./|/$', '', request.form['dest'])
        file = request.files['file']
        name = secure_filename(file.filename)
        path = os.path.join(folder.repo.path, folder.path, dest)
        os.makedirs(path, exist_ok=True)
        file.save(os.path.join(path, name))
        return {'success': True, 'name': name}
    elif action == 'dnd':
        json = request.json
        for rule in json['rules']:
            if rule['op'] in ['cp', 'mv']:
                from_ = re.sub('^/|\.\./|/$', '', rule['from']).strip()
                to = re.sub('^/|\.\./|/$', '', rule['to']).strip()
                src_path = os.path.join(folder.repo.path, folder.path, from_)
                dst_path = os.path.join(folder.repo.path, folder.path, to)
                if os.path.isfile(src_path):
                    shutil.copy(src_path, dst_path)
                    if rule['op'] == 'mv':
                        os.remove(src_path)
                    continue
                dst_path = os.path.join(dst_path, os.path.basename(src_path))
                for src_dir, _, files, in os.walk(src_path):
                    dst_dir = src_dir.replace(src_path, dst_path)
                    if not os.path.exists(dst_dir):
                        os.mkdir(dst_dir)
                    for file in files:
                        src = os.path.join(src_dir, file)
                        dst = os.path.join(dst_dir, file)
                        shutil.copy(src, dst)
                        if rule['op'] == 'mv':
                            os.remove(src)
            elif rule['op'] == 'rmtree':
                path = re.sub('^/|\.\./|/$', '', rule['path']).strip()
                path = os.path.join(folder.repo.path, folder.path, path)
                shutil.rmtree(path)
        return {'success': True}
    elif action == 'rename':
        json = request.json
        path = re.sub('^/|\.\./|/$', '', json['path']).strip()
        name = re.sub('\.\.|/', '', json['name']).strip()
        src_path = os.path.join(folder.repo.path, folder.path, path)
        dst_path = os.path.join(os.path.dirname(src_path), name)
        if os.path.exists(dst_path):
            return {'success': False}
        os.rename(src_path, dst_path)
        return {'success': True, 'name': name}
