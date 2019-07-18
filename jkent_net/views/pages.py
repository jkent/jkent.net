from ..models import Page, db
from ..subtree import subtree
from flask import Blueprint, Markup, Response, abort, current_app, render_template, request, send_file
from flask_menu import current_menu
from functools import partial

__all__ = ['bp']

bp = Blueprint('pages', __name__)


@bp.before_app_first_request
def register_menu_items():
    for page in Page.query:
        item = current_menu.submenu(page.menu_path)
        item._endpoint = 'pages.pages'
        item._endpoint_arguments_constructor = partial(lambda p: {'name': p}, page.name)
        item._text = page.title
        item._order = page.menu_order

@bp.route('/<string:name>/_<string:version>/<path:path>', methods=('POST', 'GET'))
@bp.route('/<string:name>/_<string:version>/', methods=('POST', 'GET'))
@bp.route('/<string:name>/_<string:version>', methods=('POST', 'GET'))
@bp.route('/<string:name>/<path:path>', methods=('POST', 'GET'))
@bp.route('/<string:name>/', methods=('POST', 'GET'))
@bp.route('/<string:name>', methods=('POST', 'GET'))
def pages(name, path='', version=None):
    page = Page.query.filter_by(name=name).first()
    if not page:
        abort(404)

    return subtree(page, path, version)