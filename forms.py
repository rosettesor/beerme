from flask.ext.wtf import Form, PasswordField, BooleanField, validators, Required, TextField
from flask.ext.wtf.html5 import IntegerRangeField
from wtforms import TextField, validators as v, Form, BooleanField, PasswordField
import model


# http://pythonhosted.org/Flask-WTF/
# http://flask.pocoo.org/docs/patterns/wtforms/
# http://wtforms.simplecodes.com/docs/1.0.3/crash_course.html#displaying-errors


class LoginForm(Form):
	email = TextField('email', validators=[v.required()])
	password = PasswordField('password', validators=[v.required()])


class RegistrationForm(Form):
	username = TextField('username', validators=[v.Length(max=40), v.required()])
	email = TextField('email', validators=[v.required()])
	password = PasswordField('password', validators=[v.required()])
	age = TextField('age')
	city = TextField('city')
	state = TextField('state')


class AddBeerForm(Form):
	name = TextField('name', validators=[v.required()])
	brewer = TextField('brewer', validators=[v.required()])
	origin = TextField('origin', validators=[v.required()])
	style = TextField('style', validators=[v.required()])
	abv = TextField('abv', validators=[v.Length(max=4), v.required()])
	link = TextField('link', validators=[v.required()])
	image = TextField('image', validators=[v.required()])