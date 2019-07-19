from .. import user_datastore
from ..models import db, OAuth, User
from flask import flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.google import make_google_blueprint
from flask_security import current_user, login_user

__all__ = ['bp']


bp = make_google_blueprint(reprompt_select_account=True, scope=(
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
))
bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


@oauth_authorized.connect_via(bp)
def google_logged_in(blueprint, token):
    if not token:
        flash('Failed to login with Google', category='error')
        return False

    resp = blueprint.session.get('https://openidconnect.googleapis.com/v1/userinfo')
    if not resp.ok:
        flash('Failed to fetch user info from Google', category='error')

    user_info = resp.json()
    
    if not user_info.get('email_verified'):
        flash('Email address has not been verified by Google', category='error')
        return False

    user = user_datastore.find_user(email=user_info['email'])
    if not user:
        user = user_datastore.create_user(
            email = user_info['email'],
            name = user_info['name']
        )

    oauth = OAuth.query.filter_by(
        provider = blueprint.name,
        user_id = user.id,
    ).first()
    
    if not oauth:
        oauth = OAuth(
            provider = blueprint.name,
            user = user,
            token = token,
        )

    db.session.add_all((user, oauth))
    db.session.commit()

    user.init_avatar(user, user_info['picture'] + '?size=64')

    login_user(user)
    return False