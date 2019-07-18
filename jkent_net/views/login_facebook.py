from .. import user_datastore
from ..models import db, OAuth, User
from flask import flash, url_for
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_security import current_user, login_user

__all__ = ['bp']


bp = make_facebook_blueprint(scope='email')
bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


@oauth_authorized.connect_via(bp)
def facebook_logged_in(blueprint, token):
    if not token:
        flash('Failed to login with Facebook', category='error')
        return False

    resp = blueprint.session.get("/me?fields=name,email,picture")
    if not resp.ok:
        flash('Failed to fetch user info from Facebook', category='error')

    user_info = resp.json()
    
    if not user_info.get('email'):
        flash('No email address provided by Facebook', category='error')
        return False

    user = user_datastore.find_user(email=user_info['email'])
    if not user:
        user = user_datastore.create_user(
            email = user_info['email'],
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

    user.init_avatar(user, user_info['picture']['data']['url'])

    login_user(user)
    return False