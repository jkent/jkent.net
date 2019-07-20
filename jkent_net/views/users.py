from flask import Blueprint, render_template
from flask_menu import current_menu, register_menu
from flask_security import login_required, roles_accepted
from flask_security.core import current_user

__all__ = ['bp']

bp = Blueprint('users', __name__)


@bp.before_app_first_request
def setup_menus():
    current_menu.submenu('.user.admin').register('admin.settings', 'Admin',
        order=1, visible_when=lambda: current_user.any_role('admin'))
    current_menu.submenu('.user.register').register('security.register',
        'Register', visible_when=lambda: not current_user.is_authenticated)
    current_menu.submenu('.user.login').register('security.login', 'Login',
        order=999, visible_when=lambda: not current_user.is_authenticated)
    current_menu.submenu('.user.logout').register('security.logout', 'Logout',
        order=999, visible_when=lambda: current_user.is_authenticated)

@bp.route('/profile')
@register_menu(bp, '.user.profile', 'Profile',
    visible_when=lambda: current_user.is_authenticated)
@login_required
def profile():
    return render_template('base.html')