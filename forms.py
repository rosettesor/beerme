from flask.ext.wtf import Form, PasswordField, BooleanField, validators, Required
from flask.ext.wtf.html5 import IntegerRangeField
from wtforms import TextField, validators as v, Form, BooleanField, PasswordField
import model


class LoginForm(Form):
	email = TextField('email', validators = [Required(), v.Email()])
	password = PasswordField('password', validators = [Required()])


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