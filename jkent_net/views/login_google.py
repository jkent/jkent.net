from ..models import db, OAuth, User
from flask import flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.google import make_google_blueprint
from flask_security import current_user, login_user

__all__ = ['bp']


bp = make_google_blueprint(reprompt_select_account=True, scope='email')
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

    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            email = user_info['email'],
            name = user_info['name'],
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

    user.init_avatar(user, user_info['picture'] + '?size=64')

    login_user(user)
    return False