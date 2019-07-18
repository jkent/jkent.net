from .models import Page, Subtree, User, db
from . import user_datastore
import click
from flask.cli import with_appcontext


@click.command('add-user')
@click.argument('email')
@click.password_option(prompt=False)
@click.option('--is-admin', is_flag=True)
@with_appcontext
def add_user_command(email, password=None, is_admin=False):
    """Adds a new user."""
    user = user_datastore.create_user(email=email, password=password)
    db.session.commit()
    return user


@click.command('del-user')
@click.argument('email')
@with_appcontext
def del_user_command(email):
    """Deletes a user."""
    user = user_datastore.find_user(email=email)
    user_datastore.delete_user(user)
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
    ctx.invoke(add_user_command, email='user@example.com', password='password')
    user = ctx.invoke(add_user_command, email='admin@example.com', password='password', is_admin=True)
    #user = ctx.invoke(add_user_command, email='jeff@jkent.net', password='password', is_admin=True)

    subtree = Subtree(user)
    page = Page(subtree, 'about', '.about', 'About')
    db.session.add(subtree)
    db.session.add(page)
    subtree.write('index.md', b'# About\n\nHi there, I\'m Jeff Kent! I am a digital wizard.  I contribute to a handful of open\nsource projects, design and build things (such as the engine that powers this site!),\nand just geek out.')
    subtree.commit()

    subtree = Subtree(user)
    page = Page(subtree, 'connect', '.connect', 'Connect')
    db.session.add(subtree)
    db.session.add(page)
    subtree.write('index.md', b'# Connect\n\nWant to connect with me?  Here is a non-exhaustive list of the ways you can!\n\n[<i class="fas fa-at"></i> E-mail](mailto:jeff@jkent.net)<br>\n[<i class="fab fa-facebook"></i> Facebook](https://www.facebook.com/jeff.kent.9638)<br>\n[<i class="fab fa-github"></i> GitHub](https://github.com/jkent)<br>\n[<i class="fas fa-comment-dots"></i> IRC](https://kiwiirc.com/nextclient/#irc://irc.jkent.net:+6697/#UnderGND)<br>\n[<i class="fab fa-reddit"></i> Reddit](https://reddit.com/user/jakent)<br>\n[<i class="fab fa-twitter"></i> Twitter](https://twitter.com/jkent_net)<br>')
    subtree.commit()
 
    db.session.commit()


def init_app(app):
    app.cli.add_command(add_user_command)
    app.cli.add_command(del_user_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_demo_command)
