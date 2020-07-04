from .models import User, db
from .folder import Folder
from . import user_datastore
import click
from flask import current_app
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Creates and initializes a database."""
    db.create_all()

@click.command('create-user')
@click.argument('email')
@click.password_option(prompt=False)
@click.option('--is-admin', is_flag=True)
@click.pass_context
@with_appcontext
def create_user_command(ctx, email, password=None, is_admin=False):
    """Creates a new user."""
    user = user_datastore.create_user(email=email, password=password)
    if is_admin:
        ctx.invoke(add_role_command, email=email, name='admin')
    db.session.commit()
    return user

@click.command('delete-user')
@click.argument('email')
@with_appcontext
def delete_user_command(email):
    """Deletes a user."""
    user = user_datastore.find_user(email=email)
    user_datastore.delete_user(user)
    db.session.commit()

@click.command('create-role')
@click.argument('name')
@click.argument('description')
@with_appcontext
def create_role_command(name, description=None):
    """Creates a role."""
    user_datastore.create_role(name=name, description=description)
    db.session.commit()

@click.command('add-role')
@click.argument('email')
@click.argument('name')
@with_appcontext
def add_role_command(email, name):
    """Adds a role to a user."""
    user_datastore.add_role_to_user(email, name)
    db.session.commit()

@click.command('remove-role')
@click.argument('email')
@click.argument('name')
@with_appcontext
def remove_role_command(email, name):
    """Remove a role from a user."""
    user_datastore.remove_role_from_user(email, name)
    db.session.commit()

@click.command('create-folder')
@with_appcontext
def create_tree_command():
    """Create a folder."""
    tree = Folder.create(current_app.repo)

def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(delete_user_command)
    app.cli.add_command(create_role_command)
    app.cli.add_command(add_role_command)
    app.cli.add_command(create_tree_command)