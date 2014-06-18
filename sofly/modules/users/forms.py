from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, EqualTo, Email

class LoginForm(Form):
    email = TextField('Email address', [Required(), Email()])
    password = PasswordField('Password', [Required()])

class RegisterForm(Form):
    first_name = TextField('First name', [Required()])
    last_name = TextField('Last name', [Required()])
    email = TextField('Email address', [Required(), Email()])
    password = PasswordField('Password', [Required()])
    confirm = PasswordField('Confirm Password', [
            Required(),
            EqualTo('password', message='Passwords must match')
            ])
    #accept_tos = BooleanField('I accept the TOS', [Required()])
    recaptcha = RecaptchaField()

class UserForm(Form):
    first_name = TextField('First name', [Required()])
    last_name = TextField('Last name', [Required()])
    email = TextField('Email address', [])
    password = PasswordField('Password', [Required()])