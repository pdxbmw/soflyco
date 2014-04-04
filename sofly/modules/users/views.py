from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

from authomatic import Authomatic
from authomatic.adapters import WerkzeugAdapter
from bson import ObjectId
from itsdangerous import BadSignature
from werkzeug import check_password_hash, generate_password_hash

from sofly import db, mail, security
from sofly.modules.users.forms import RegisterForm, LoginForm
from sofly.modules.users.models import User
from sofly.modules.users.decorators import login_required
from sofly.modules.results.models import Watch
from sofly.utils.alaska import Itinerary

module = Blueprint('users', __name__, url_prefix='/users')

@module.before_request
def before_request():
    """
    Pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.objects.get(id=ObjectId(session['user_id']))

@module.route('/me/')
@login_required
def home():
    watched = Watch.objects(watchers__email=g.user.email).no_dereference()
    claims, refunded = 0, 0
    itineraries = []
    for watch in watched:
        itinerary = Itinerary().from_identifier(watch.identifier)
        itinerary.price = watch.prices[-1].price
        for watcher in watch.watchers:
            if watcher.email == g.user.email:
                itinerary.claims = watcher.claims
                itinerary.paid = watcher.reservation['paid']
                claims += len(watcher.claims)
                if len(watcher.claims):
                    refunded += float(watcher.reservation['paid']) - \
                                float(watcher.claims[-1]['price'])
                    itinerary.refunded = refunded
                break
        itineraries.append(itinerary)                
    context = dict(
        user = g.user,
        claims = claims,
        refunded = refunded,
        itineraries = itineraries,
        watching = watched
    )
    return render_template('users/profile.html', **context)

@module.route('/activate')
@login_required
def activation_email():
    if g.user:
        mail.send_activation_email()
        flash("An email has been sent to verify your email address.", 'info')
    return redirect(url_for('users.home')) 

@module.route('/activate/<payload>')
def activate_user(payload):
    s = security.get_serializer()
    try:
        user_id = s.loads(payload)
    except BadSignature:
        abort(404)
    
    user = User.objects.get(id=ObjectId(user_id))
    user.verified = True
    user.save()
    
    flash("Thank you, %s. You can now receive alerts." % user.first_name, 'success')
    
    return redirect(url_for('users.home')) 


@module.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    form = LoginForm(request.form)
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        user = User.objects.filter(email=form.email.data).first()
        # we use werzeug to validate user's password
        if user and check_password_hash(user.password, form.password.data):
            # the session can't be modified as it's signed, 
            # it's a safe place to store the user id
            if not user.verified:
                flash("Your email address has not been verified. \
                    <a href=\"%s\">Click here to resend the verification email</a>." \
                    % url_for('users.activation_email'), "warning")
            else:
                flash('Welcome back, %s!' % user.first_name, 'success')
            session['user_id'] = user.id
            return redirect(url_for('users.home'))
        flash('Wrong email or password', 'danger')
    return render_template('users/login.html', form=form)

@module.route('/login/<provider>/', methods=['GET', 'POST'])
def login_provider(provider=None):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    authomatic = Authomatic(config=config.config, 
                            secret=config.SECRET_KEY, 
                            report_errors=True,
                            logging_level=log.level)    
    response = make_response(redirect(redirect_url()))
    result = authomatic.login(WerkzeugAdapter(request, response), provider)
    if result:
        user = result.user
        if user:
            user.update()
            verified = mongoUtils.verify_user(user, provider=provider)
            if not verified:
                verified = mail.send_activation_email(email=user.email)    
                flash("Welcome to SoFly! An email has been sent to verify your email address.", 
                    category='info')
            session['user'] = dict(
                email      = user.email,
                first_name = user.first_name,
                last_name  = user.last_name,
                name       = user.name, 
                id         = user.id,
                verified   = verified
            )
            log.debug(session['user'])
    return response

@module.route('/logout')
def logout():
    # remove the username from the session if it exists
    session.pop('_flashes', None)
    flash("You were successfully logged out.", 'success')
    session.pop('user_id', None)
    return redirect(url_for('index'))      

@module.route('/register/', methods=['GET', 'POST'])
def register():
    """
    Registration Form
    """
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # create an user instance not yet stored in the database
        user = User(
            first_name = form.first_name.data, 
            last_name = form.last_name.data,
            email = form.email.data, 
            password = generate_password_hash(form.password.data)
            )
        # Insert the record in our database and commit it
        user.save()

        # Log the user in, as he now has an id
        session['user_id'] = user.id
        
        # flash will display a message to the user
        flash("Welcome to SoFly! An email has been sent to verify your email address.", 'info')        
        mail.send_activation_email(user=user)
        
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('users.home'))
    return render_template("users/register.html", form=form)    