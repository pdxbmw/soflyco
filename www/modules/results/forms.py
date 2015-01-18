from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, EqualTo

class OneForm(Form):
    pass

class MultiForm(Form):
    pass