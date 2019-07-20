from flask import Blueprint, Markup, Response, abort, current_app, render_template, request, send_file

__all__ = ['bp']

bp = Blueprint('admin', __name__)

@bp.route('')
def index():
    return render_template('admin/index.html')

@bp.route('pages')
def pages():
    return render_template('admin/pages.html')