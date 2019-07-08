import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from jkent_net.models import User, db


@click.command('add-user')
@click.argument('email')
@click.password_option()
@click.option('--is-admin', is_flag=True)
@with_appcontext
def add_user_command(email, password, is_admin):
    """Adds a new user."""
    hash = generate_password_hash(password)
    user = User(email=email, hash=hash, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()


@click.command('del-user')
@click.argument('email')
@with_appcontext
def del_user_command(email):
    """Deletes a user."""
    user = User.query.filter_by(email=email)
    if user is None:
        print('no such user exists!')
        return

    user.delete()
    db.session.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Creates and initializes a database"""
    db.create_all()


def init_app(app):
    app.cli.add_command(add_user_command)
    app.cli.add_command(del_user_command)
    app.cli.add_command(init_db_command)
