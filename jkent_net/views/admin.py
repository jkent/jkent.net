from ..models import Page, Role, User
from ..utils import Pager
from flask import Blueprint, render_template, request
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
@register_menu(bp, '.admin.pages', 'Pages',
    visible_when=lambda: current_user.any_role('admin', 'editor'),
    active_when=lambda: request.endpoint.startswith('admin.pages_'))
def pages_index():
    pager = Pager(20, Page.query.count())
    pager.page = int(request.args.get('page', pager.first))
    pages = Page.query.order_by(Page.name).offset(pager.offset).limit(pager.items_per_page).all()
    return render_template('admin/pages_index.html', pager=pager, pages=pages)

@bp.route('pages/<string:id>')
@roles_accepted('admin', 'editor')
@register_menu(bp, '.admin.pages.edit', 'Edit')
def pages_edit(id):
    return render_template('admin/pages_edit.html')

@bp.route('roles')
@roles_accepted('admin')
@register_menu(bp, '.admin.roles', 'Roles',
    visible_when=lambda: current_user.any_role('admin'),
    active_when=lambda: request.endpoint.startswith('admin.roles_'))
def roles_index():
    pager = Pager(20, Role.query.count())
    pager.page = int(request.args.get('page', pager.first))
    roles = Role.query.order_by(Role.description).offset(pager.offset).limit(pager.items_per_page).all()
    return render_template('admin/roles_index.html', pager=pager, roles=roles)

@bp.route('roles/<int:id>')
@roles_accepted('admin')
@register_menu(bp, '.admin.roles.edit', 'Edit')
def roles_edit(id):
    return render_template('admin/roles_edit.html')

@bp.route('users')
@roles_accepted('admin')
@register_menu(bp, '.admin.users', 'Users',
    visible_when=lambda: current_user.any_role('admin'),
    active_when=lambda: request.endpoint.startswith('admin.users_'))
def users_index():
    pager = Pager(20, User.query.count())
    pager.page = int(request.args.get('page', pager.first))
    users = User.query.order_by(User.name, User.email).offset(pager.offset).limit(pager.items_per_page).all()
    return render_template('admin/users_index.html', pager=pager, users=users)

@bp.route('users/<int:id>')
@roles_accepted('admin')
@register_menu(bp, '.admin.users.edit', 'Edit')
def users_edit(id):
    return render_template('admin/users_edit.html')