from ..models import Page, db
from ..subtree import subtree
from ..utils import update_menus
from flask import Blueprint, abort

__all__ = ['bp']

bp = Blueprint('pages', __name__)


@bp.before_app_first_request
def register_menu_items():
    update_menus()

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