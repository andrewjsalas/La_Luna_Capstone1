"""Login and Register Forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, validators
from wtforms.validators import InputRequired, Length, NumberRange, Optional, DataRequired


class LoginForm(FlaskForm):
    """User Login Form"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=1, max=15)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)],
    )


class RegisterForm(FlaskForm):
    """Form for user registration"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=1, max=15)],
    )
    name = StringField(
        "Name",
        validators=[InputRequired(), Length(max=25)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)],
    )


class UserEditForm(FlaskForm):
    """Form for editing users"""

    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(max=25)])
    password = PasswordField('Password', validators=[Length(min=6, max=100)])
