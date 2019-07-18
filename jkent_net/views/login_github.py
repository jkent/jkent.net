from .. import user_datastore
from ..models import db, OAuth, User
from flask import flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.github import make_github_blueprint
from flask_security import current_user, login_user

__all__ = ['bp']


bp = make_github_blueprint(scope='user:email')
bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


@oauth_authorized.connect_via(bp)
def github_logged_in(blueprint, token):
    if not token:
        flash('Failed to login with GitHub', category='error')
        return False

    resp = blueprint.session.get('/user')
    if not resp.ok:
        flash('Failed to fetch user info from GitHub', category='error')

    user_info = resp.json()

    resp = blueprint.session.get('/user/emails')
    if not resp.ok:
        flash('Failed to fetch email info from GitHub', category='error')
        return False

    entries = resp.json()
    entries = sorted(entries, key=lambda e: not e['primary'])
    entries = list(filter(lambda e: e['verified'], entries))

    if not entries:
        flash('No email addresses have been verified by GitHub', category='error')
        return False

    user = None
    for entry in entries:
        user = user_datastore.find_user(email=entry['email'])
        if user:
            break

    if not user:
        user = user_datastore.create_user(
            email = entries[0]['email'],
            name = user_info['name']
        )

    oauth = OAuth.query.filter_by(
        provider = blueprint.name,
        user = user,
    ).first()
    
    if not oauth:
        oauth = OAuth(
            provider = blueprint.name,
            user = user,
            token = token,
        )

    db.session.add_all([user, oauth])
    db.session.commit()

    user.init_avatar(user, user_info['avatar_url'] + '&s=64')

    login_user(user)
    return False