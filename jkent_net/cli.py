import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from jkent_net.models import Page, Subtree, User, db


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
    return user


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
    """Creates and initializes a database."""
    db.create_all()


@click.command('init-demo')
@click.pass_context
@with_appcontext
def init_demo_command(ctx):
    """Initializes everything for a demo."""
    ctx.invoke(init_db_command)
    user = ctx.invoke(add_user_command, email='user@example.com', password='password', is_admin=True)
    subtree = Subtree(user)
    db.session.add(subtree)
    subtree.write('index.md', b'# Hello world!\n\nThis is in the HEAD~1')
    subtree.commit('first commit')
    subtree.write('index.md', b'# Hello world!\n\nThis is in the HEAD')
    subtree.commit('second commit')
    subtree.write('index.md', b'# Hello world!\n\nThis is in the index')
    page = Page(subtree, 'test', '.test', 'Test')
    db.session.add(page)
    db.session.commit()


def init_app(app):
    app.cli.add_command(add_user_command)
    app.cli.add_command(del_user_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_demo_command)