from ..models import db, Role, User
from ..utils import Pager
from flask import Blueprint, redirect, render_template, request, url_for
from flask_menu import current_menu, register_menu
from flask_security import roles_accepted
from flask_security.core import current_user
from sqlalchemy.sql.functions import concat

__all__ = ['bp']

bp = Blueprint('admin', __name__)

RESULTS_PER_PAGE = 20


@bp.route('settings')
@roles_accepted('admin')
@register_menu(bp, '.admin.settings', 'Settings', visible_when=lambda: current_user.any_role('admin'))
def settings():
    return render_template('admin/settings.html')



@bp.route('roles')
@roles_accepted('admin')
@register_menu(bp, '.admin.roles', 'Roles',
    visible_when=lambda: current_user.any_role('admin'),
    active_when=lambda: request.endpoint.startswith('admin.roles_'))
def roles_index():
    return render_template('admin/roles_index.html')

@bp.route('roles/json')
@roles_accepted('admin')
def roles_json():
    pager = Pager(20)
    pager.page = int(request.args.get('pg', pager.first))
    query = Role.query
    q = request.args.get('q', None)
    if q:
        query = query.filter(Role.searchable.contains(q))
    pager.items = query.count()
    query = query.order_by(Role.name, Role.description)
    query = query.offset(pager.offset).limit(pager.items_per_page)
    roles = query.all()
    entries = []
    for role in roles:
        entries.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
        })
    return {
        'entries': entries,
        'items_per_page': pager.items_per_page,
        'num_pages': pager.count,
    }

@bp.route('roles/validate', methods=('POST',))
@roles_accepted('admin')
def roles_validate():
    role = Role.query.filter_by(name=request.form.get('name')).first()
    return {'exists': role != None}

@bp.route('roles/<int:id>', methods=('GET', 'POST'))
@roles_accepted('admin')
@register_menu(bp, '.admin.roles.edit', 'Edit')
def roles_edit(id):
    role = Role.query.get(id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            db.session.delete(role)
            db.session.commit()
        elif action == 'save':
            role.name = request.form['name'].strip()
            role.description = request.form['description'].strip()
            db.session.add(role)
            db.session.commit()

        subquery = db.session.query(Role.id,db.func.ROW_NUMBER() \
            .over(order_by=(Role.name,Role.description)).label('n')).subquery()
        query = db.session.query((subquery.c.n-1)) \
            .join(Role, Role.id==subquery.c.id).filter(subquery.c.id==id)
        results = query.first()
        pagenum = (results[0] // RESULTS_PER_PAGE) + 1 if results else 1
        return redirect(url_for('admin.roles_index') + '#pg={}'.format(pagenum))

    return render_template('admin/roles_edit.html', role=role)

@bp.route('roles/new', methods=('POST',))
@roles_accepted('admin')
def roles_new():
    name = request.form.get('name')
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return redirect(url_for('admin.roles_edit', id=role.id))



@bp.route('users')
@roles_accepted('admin')
@register_menu(bp, '.admin.users', 'Users',
    visible_when=lambda: current_user.any_role('admin'),
    active_when=lambda: request.endpoint.startswith('admin.users_'))
def users_index():
    return render_template('admin/users_index.html')

@bp.route('users/json')
@roles_accepted('admin')
def users_json():
    pager = Pager(20)
    pager.page = int(request.args.get('pg', pager.first))
    query = User.query
    q = request.args.get('q', None)
    if q:
        query = query.filter(User.searchable.contains(q))
    pager.items = query.count()
    query = query.order_by(User.name, User.email)
    query = query.offset(pager.offset).limit(pager.items_per_page)
    users = query.all()
    entries = []
    for user in users:
        entries.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
        })
    return {
        'entries': entries,
        'items_per_page': pager.items_per_page,
        'num_pages': pager.count,
    }

@bp.route('users/<int:id>', methods=('GET', 'POST'))
@roles_accepted('admin')
def users_edit(id):
    user = User.query.get(id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            db.session.delete(user)
            db.session.commit()
        elif action == 'save':
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            roles = request.form.get('roles', '').split(',')
            roles_list = []
            for role in roles:
                role = Role.query.filter_by(name=role).first()
                if role:
                    roles_list.append(role)
            user.roles = roles_list
            db.session.add(user)
            db.session.commit()

        subquery = db.session.query(User.id,db.func.ROW_NUMBER() \
            .over(order_by=(User.name,User.email)).label('n')).subquery()
        query = db.session.query((subquery.c.n-1)) \
            .join(User, User.id==subquery.c.id).filter(subquery.c.id==id)
        results = query.first()
        pagenum = (results[0] // RESULTS_PER_PAGE) + 1 if results else 1
        return redirect(url_for('admin.users_index') + '#pg={}'.format(pagenum))

    return render_template('admin/users_edit.html', user=user)

@bp.route('users/new', methods=('POST',))
@roles_accepted('admin')
def users_new():
    email = request.form.get('email')
    user = User(email=email)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin.users_edit', id=user.id))