from flask import g, flash, redirect, url_for, request

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash(u'You need to be signed in for this page.', 'warning')
            return redirect(url_for('users.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function