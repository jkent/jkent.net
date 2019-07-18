from ..models import db, OAuth, User
from flask import flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.github import make_github_blueprint
from flask_security import current_user, login_user

__all__ = ['bp']

bp = make_github_blueprint()
bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

@oauth_authorized.connect_via(bp)
def github_logged_in(blueprint, token):
    if not token:
        flash('Failed to login with GitHub', category='error')
        return False

    resp = blueprint.session.get('/user')
    if not resp.ok:
        flash('Failed to fetch user info from GitHub', category='error')
        return False

    github_info = resp.json()
    github_user_id = str(github_info['id'])
    
    query = OAuth.query.filter_by(
        provider = blueprint.name,
        provider_user_id = github_user_id,
    )

    oauth = query.first()
    if not oauth:
        oauth = OAuth(
            provider = blueprint.name,
            provider_user_id = github_user_id,
            token = token,
        )
    
    if oauth.user:
        login_user(oauth.user)
    else:
        user = User(
            email = github_info['email'],
            name = github_info['name'],
        )
        oauth.user = user
        db.session.add_all((user, oauth))
        db.session.commit()

        login_user(user)