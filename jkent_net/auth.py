from flask import abort, flash, g, redirect, request, url_for
from functools import wraps
from jkent_net.models import User


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if g.user is None:
            flash("Please login to continue.")
            return redirect(url_for('auth.login', r=None if request.path == '/' else request.path))
        return f(*args, **kwargs)
    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if g.user is None:
            flash("Please login to continue.")
            return redirect(url_for('auth.login', r=None if request.path == '/' else request.path))
        if not g.user.is_admin:
            flash("Unauthorized.")
            abort(403)
        return f(*args, **kwargs)
    return wrap