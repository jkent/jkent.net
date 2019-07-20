from flask import Blueprint, render_template
from flask_menu import current_menu, register_menu


__all__ = ['bp']

bp = Blueprint('admin', __name__)

@bp.route('settings')
@register_menu(bp, '.admin.settings', 'Settings')
def settings():
    return render_template('admin/settings.html')

@bp.route('pages')
@register_menu(bp, '.admin.pages', 'Pages')
def pages():
    return render_template('admin/pages.html')

@bp.route('users')
@register_menu(bp, '.admin.users', 'Users')
def users():
    return render_template('admin/users.html')