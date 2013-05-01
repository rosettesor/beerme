from flask.ext.wtf import Form, PasswordField, BooleanField, validators, Required
from flask.ext.wtf.html5 import IntegerRangeField
from wtforms import TextField, validators, Form, BooleanField, PasswordField
import model


class LoginForm(Form):
	email = TextField('email', [validators.Length(min=6, max=35)])
	password = PasswordField('password', validators.Required())

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])


# http://pythonhosted.org/Flask-WTF/
# http://flask.pocoo.org/docs/patterns/wtforms/
# http://wtforms.simplecodes.com/docs/1.0.3/crash_course.html#displaying-errors


# class Registration(Form):
#   email = TextField("email", validators=[v.required()])
#   password = PasswordField("password",[v.required(), v.EqualTo('confirm', message='passwords must match')])
#   confirm = PasswordField('repeat password')
#   username = TextField("username", validators=[v.required()])
#   age = TextField("age", validators=[v.required()])
#   city = TextField("city", validators=[v.required()])
#   state = TextField("state", validators=[v.required()])


# BANGING
# HEAD
# AGAINST
# WALL