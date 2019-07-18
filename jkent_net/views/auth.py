from jkent_net.models import User, UserImageSource, db
from jkent_net.utils import get_redirect_target
from flask import Blueprint, flash, current_app, g, redirect, render_template, request, session, url_for
from google_auth_oauthlib.flow import Flow
import hashlib
import json
import jwt
import os
import random
import string
from urllib.parse import urlencode
from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse, url_join

__all__ = ['bp']


bp = Blueprint('auth', __name__)

@bp.before_app_first_request
def load_secrets():
    global google_client_config

    with open(os.path.join(current_app.instance_path, 'google_client_secret.json'), 'r') as json_file:
        google_client_config = json.load(json_file)

def random_string(length=10):
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(length))

rs = random_string(40)

def get_flow(state=None):
    flow = Flow.from_client_config(
        google_client_config,
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
        ],
        state=state,
    )

    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)
    flow.code_verifier = rs
    return flow

@bp.route('/login', methods=('GET', 'POST'))
def login():
    r = get_redirect_target('index')
    if g.user:
        return redirect(request.args.get('r', r))

    if request.method == 'POST':
        r = session.get('auth_redirect', url_for('index'))
        email = request.form.get('email')
        password = request.form.get('password')

        g.user = User.query.filter_by(email=email).first()
        if g.user is None or g.user.hash is None or not check_password_hash(g.user.hash, password):
            flash('Invalid user or password.')
            return redirect(url_for('auth.login', r=r))

        session['auth_email'] = email
        session['auth_picture'] = url_for('static', filename='user.png')
        if g.user.image_source in [UserImageSource.auto, UserImageSource.upload] and False:
            pass # TODO: handle image uploads
        elif g.user.image_source in [UserImageSource.auto, UserImageSource.gravitar]:
            hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
            url = url_for('static', filename='user.png', _external=True)
            url = 'https://www.gravatar.com/avatar/{}?{}'.format(hash, urlencode({'d': url, 's': 32}))
            session['auth_picture'] = url

        del session['auth_redirect']
        return redirect(r)
    
    provider = request.args.get('provider')
    if provider == 'google':
        flow = get_flow()

        authorization_url, state = flow.authorization_url(
            access_type = 'offline',
            include_granted_scopes = 'true',
            prompt = 'select_account',
        )

        session['auth_provider'] = provider
        session['auth_state'] = state

        return redirect(authorization_url)
    else:
        session['auth_redirect'] = r
        return render_template('auth/login.html')

@bp.route('/register')
def register():
    if g.user:
        return redirect(url_for('index'))
    
    return render_template('auth/base.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/oauth2callback')
def oauth2callback():
    r = session.get('auth_redirect', url_for('index'))

    error = request.args.get('error')
    if error:
        return redirect(url_for('index'))

    if session['auth_provider'] == 'google':
        flow = get_flow(session['auth_state'])
        flow.fetch_token(authorization_response=request.url)

        data = jwt.decode(flow.credentials.id_token, verify=False)
        if 'email' not in data or not data['email_verified']:
            flash('Email missing or is unverified')
            return redirect(url_for('auth.login', r=r))
      
        email = session['auth_email'] = data['email']
        g.user = User.query.filter_by(email=email).first()
        if g.user is None:
            g.user = User(email=email, hash=hash, name = data['name'], is_admin=False)

        session['auth_picture'] = url_for('static', filename='user.png')
        if g.user.image_source in [UserImageSource.auto, UserImageSource.upload] and False:
            pass # TODO: handle image uploads
        elif g.user.image_source in [UserImageSource.auto, UserImageSource.oauth2] and \
                'picture' in data:
            session['auth_picture'] = data['picture']
        elif g.user.image_source in [UserImageSource.auto, UserImageSource.gravitar]:
            hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
            url = url_for('static', filename='user.png', _external=True)
            url = 'https://www.gravatar.com/avatar/{}?{}'.format(hash, urlencode({'d': url, 's': 32}))
            session['auth_picture'] = url

    del session['auth_redirect']
    return redirect(r)