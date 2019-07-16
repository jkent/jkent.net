from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
import hashlib
from urllib.parse import urlencode
from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse, url_join
from jkent_net.models import User, db
from jkent_net.utils import get_redirect_target

__all__ = ['bp']


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    r = get_redirect_target('posts.index')
    if g.user:
        return redirect(request.args.get('r', r))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        g.user = User.query.filter_by(email=email).first()
        if g.user is None or not check_password_hash(g.user.hash, password):
            flash('Invalid user or password.')
            return redirect(url_for('auth.login', r=session['auth_redirect']))

        session['auth_email'] = email

        hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
        url = url_for('static', filename='user.png', _external=True)
        url = 'https://www.gravatar.com/avatar/{}?{}'.format(hash, urlencode({'d': url, 's': 32}))
        session['auth_picture'] = url

        r = session['auth_redirect']
        del session['auth_redirect']
        return redirect(r)

    session['auth_redirect'] = r
    return render_template('auth/login.html')

@bp.route('/register')
def register():
    if g.user:
        return redirect(url_for('posts.index'))
    
    return render_template('auth/base.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('posts.index'))