from .models import Page, Subtree, User, db
from . import user_datastore
import click
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

@click.command('init-demo')
@click.pass_context
@with_appcontext
def init_demo_command(ctx):
    """Initializes everything for a demo."""
    ctx.invoke(init_db_command)
    ctx.invoke(create_role_command, name='admin', description='Administrator')
    ctx.invoke(create_user_command, email='user@example.com', password='password')
    ctx.invoke(create_user_command, email='admin@example.com', password='password', is_admin=True)
    user = ctx.invoke(create_user_command, email='jeff@jkent.net', is_admin=True)

    subtree = Subtree(user)
    page = Page(subtree, 'about', '.about', 'About')
    db.session.add(subtree)
    db.session.add(page)
    subtree.write('index.md', b'Hi there, I\'m Jeff Kent! I am a digital wizard.  I contribute to a handful of open\nsource projects, design and build things (such as the engine that powers this site!),\nand just geek out.')
    subtree.commit()

    subtree = Subtree(user)
    page = Page(subtree, 'connect', '.connect', 'Connect')
    db.session.add(subtree)
    db.session.add(page)
    subtree.write('index.md', b'Want to connect with me?  Here is a non-exhaustive list of the ways you can!\n\n[<i class="fas fa-at"></i> E-mail](mailto:jeff@jkent.net)<br>\n[<i class="fab fa-facebook"></i> Facebook](https://www.facebook.com/jeff.kent.9638)<br>\n[<i class="fab fa-github"></i> GitHub](https://github.com/jkent)<br>\n[<i class="fas fa-comment-dots"></i> IRC](https://kiwiirc.com/nextclient/#irc://irc.jkent.net:+6697/#UnderGND)<br>\n[<i class="fab fa-reddit"></i> Reddit](https://reddit.com/user/jakent)<br>\n[<i class="fab fa-twitter"></i> Twitter](https://twitter.com/jkent_net)<br>')
    subtree.commit()
 
    db.session.commit()


def init_app(app):
    app.cli.add_command(create_user_command)
    app.cli.add_command(delete_user_command)
    app.cli.add_command(create_role_command)
    app.cli.add_command(add_role_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_demo_command)
