from flask import abort, g, flash, redirect, request, session, url_for

from sofly.helpers import is_ajax

from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            if is_ajax(request):
                abort(401)
            else:
                flash(u'You need to be signed in for this page.', 'warning')
                return redirect(url_for('users.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function    

def verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user.verified:
            """
            flash("Your email address has not been verified. <a href=\"%s\"> \
                Click here to resend the verification email</a>." % url_for('users.activation_email'), 
                category="warning")
            """
            abort(403)
            return redirect(url_for(request.path))
        return f(*args, **kwargs)
    return decorated_function    

def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator    