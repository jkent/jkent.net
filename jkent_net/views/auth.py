from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
import hashlib
import jwt
import os
from urllib.parse import urlencode
from werkzeug.security import check_password_hash
from jkent_net.models import User, db

__all__ = ['bp']


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(request.args.get('r', url_for('index')))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        g.user = User.query.filter_by(email=email).first()
        if g.user is None or not check_password_hash(g.user.hash, password):
            flash('Invalid user or password.')
            return redirect(url_for('auth.login', r=session['auth_redirect']))

        session['auth_email'] = email

        hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
        url = 'https://www.gravatar.com/avatar/' + hash
        url += urlencode({'d': url_for('static', filename='images/admin.jpg', _external=True), 's': 32})
        session['auth_picture'] = url

        r = session['auth_redirect']
        del session['auth_redirect']
        return redirect(r)

    session['auth_redirect'] = request.args.get('r', url_for('index'))
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