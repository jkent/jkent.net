from flask import Blueprint, render_template
from flask_menu import current_menu, register_menu
from flask_security import roles_accepted
from flask_security.core import current_user

__all__ = ['bp']

bp = Blueprint('admin', __name__)


@bp.route('settings')
@roles_accepted('admin')
@register_menu(bp, '.admin.settings', 'Settings', visible_when=lambda: current_user.any_role('admin'))
def settings():
    return render_template('admin/settings.html')

@bp.route('pages')
@roles_accepted('admin', 'editor')
@register_menu(bp, '.admin.pages', 'Pages', visible_when=lambda: current_user.any_role('admin', 'editor'))
def pages():
    return render_template('admin/pages.html')

@bp.route('users')
@roles_accepted('admin')
@register_menu(bp, '.admin.users', 'Users', visible_when=lambda: current_user.any_role('admin'))
def users():
    return render_template('admin/users.html')