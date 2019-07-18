from jkent_net.models import db
from diff_match_patch import diff_match_patch
from flask import Markup, abort, g, redirect, render_template, request, send_file, url_for


def render(page, path, version):
    file, mimetype, fragment = page.subtree.open(path, version)
    if not file:
        abort(404)

    if not fragment:
        return send_file(file, mimetype=mimetype)

    html = file.read()

    return render_template('subtree.html', **{
        'mode': 'render',
        'page': page,
        'path': path,
        'title': page.title,
        'content': Markup(html.decode('utf8')),
        'version': version,
        'viewonly': True,
        'mimetype': page.subtree._mimetype_from_path(path) or mimetype,
    })

def raw(page, path, version):
    file, mimetype, fragment = page.subtree.open(path, version=version, raw=True)
    if not mimetype.startswith('text/'):
        return send_file(file, mimetype=mimetype)

    return render_template('subtree.html', **{
        'mode': 'raw',
        'page': page,
        'path': path,
        'title': page.title,
        'content': file.read().decode('utf8'),
        'version': version,
        'viewonly': not (g.user and g.user.is_admin),
        'mimetype': mimetype,
    })

def edit(page, path, version):
    file, mimetype, fragment = page.subtree.open(path, version=None, raw=True)
    if not mimetype.startswith('text/'):
        return send_file(file, mimetype=mimetype)

    return render_template('subtree.html', **{
        'mode': 'edit',
        'page': page,
        'path': path,
        'title': page.title,
        'content': file.read().decode('utf8'),
        'version': version,
        'viewonly': not (g.user and g.user.is_admin),
        'mimetype': mimetype,
    })

def patch(page, path):
    file, mimetype, fragment = page.subtree.open(path, version=None, raw=True)
    if not mimetype.startswith('text/'):
        return abort(400)

    dmp = diff_match_patch()
    patch = dmp.patch_fromText(request.form.get('patch'))
    text, _ = dmp.patch_apply(patch, file.read().decode('utf8'))
    page.subtree.write(path, text.encode('utf8'))

    return {
        'draft': page.subtree.diff(None, None, 'HEAD'),
    }

def subtree(page, path, version):
    request_version = version
    if version == None and not (g.user and g.user.is_admin):
        version = 'HEAD'

    if page.subtree.isdir(path, version):
        index = page.subtree.find_index(path)
        if not index:
            abort(404)
        path = index

    if request.method == 'POST' and g.user and g.user.is_admin:
        action = request.form.get('action')
        if action == 'patch':
            return patch(page, path)
        elif action == 'restore':
            page.subtree.revert(version)
            return {}
        elif action == 'commit':
            page.subtree.commit()
            return {}
        elif action == 'set-title':
            page.title = request.form.get('title')
            db.session.add(page)
            db.session.commit()
            return {}

    if request.args.get('raw'):
        return raw(page, path, version)
    elif request.args.get('edit') != None:
        return edit(page, path, version)

    return render(page, path, version)