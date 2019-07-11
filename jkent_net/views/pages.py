from flask import Blueprint, render_template
from flask_menu import register_menu

__all__ = ['bp']


bp = Blueprint('pages', __name__)

@bp.route('/about')
@register_menu(bp, '.about', 'About')
def about():
    return render_template('about.html')

@bp.route('/connect')
@register_menu(bp, '.connect', 'Connect')
def contact():
    return render_template('connect.html')