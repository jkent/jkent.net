from flask import Blueprint, Markup, Response, abort, current_app, render_template, request, send_file
from flask_menu import current_menu, register_menu
from ..models import Page, db

__all__ = ['bp']

bp = Blueprint('pages', __name__)


@bp.before_app_first_request
def register_menu_items():
    for page in Page.query:
        item = current_menu.submenu(page.menu_path)
        item._external_url = page.path
        item._text = page.title
        item._order = page.menu_order


@bp.route('/<path:path>', endpoint='*')
def pages(path):
    spath = ''

    while True:
        page = Page.query.filter_by(path=path).first()
        if page:
            break
        parts = path.rsplit('/', 1)
        if len(parts) == 1:
            abort(404)
        path, part = parts
        if spath:
            spath = part + '/' + spath
        else:
            spath = part

    if page.subtree.isdir(spath):
        index = page.subtree.find_index(spath)
        if not index:
            abort(404)
        spath = index

    file, mimetype = page.subtree.read(spath)
    if not file:
        abort(404)

    if mimetype == 'text/html':
        html = file.read()
        if html.find(b'<title>') >= 0:
            return Response(html, mimetype)

        return render_template('page_view.html', **{
            'title': page.title,
            'content': Markup(html.decode('utf8'))
        })

    return send_file(file, mimetype=mimetype)