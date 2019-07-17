from diff_match_patch import diff_match_patch
from flask import Markup, abort, g, redirect, render_template, request, send_file, url_for


def view(page, path, version):
    file, mimetype, fragment = page.subtree.open(path, version)
    if not file:
        abort(404)

    if not fragment:
        return send_file(file, mimetype=mimetype)

    html = file.read()

    return render_template('subtree_view.html', **{
        'page': page,
        'path': path,
        'title': page.title,
        'content': Markup(html.decode('utf8')),
        'version': version,
        'viewonly': True,
        'mimetype': mimetype,
    })

def editor(page, path):
    file, mimetype, fragment = page.subtree.open(path, version=None, raw=True)
    if not mimetype.startswith('text/'):
        return send_file(file, mimetype=mimetype)

    return render_template('subtree_editor.html', **{
        'page': page,
        'path': path,
        'title': page.title,
        'content': file.read().decode('utf8'),
        'version': None,
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
        'dirty': page.subtree.dirty(path),
    }

def subtree(page, path, version):
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
        elif action == 'revert':
            page.subtree.revert()
            return {}
        elif action == 'commit':
            page.subtree.commit()
            return {}

    if request.args.get('source') != None:
        if version:
            return redirect(url_for('pages.pages', page=page.path, path=path, source=1))
        return editor(page, path)

    return view(page, path, version)