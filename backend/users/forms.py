from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class MessageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = StringField('Text', validators=[DataRequired()])
    interval = StringField('Interval', validators=[DataRequired()])
    file = StringField('File')
    submit = SubmitField('Salvar')

class UserPhoneForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    phone_token = StringField('Phone Token', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')