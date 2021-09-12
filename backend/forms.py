from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, EqualTo, Length, InputRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed
from backend.models import User

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email(), InputRequired(), Length(min=6, max=256)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=32)])
    remember = BooleanField("Remember me", default=True)


class SignupForm(FlaskForm):
    email = StringField("Email", validators=[Email(), InputRequired(), Length(min=6, max=256)])
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=32)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=32)])
    confirm_password = PasswordField("Confirm Password", validators=[
        InputRequired(), Length(min=3, max=32),
        EqualTo("password", message="Passwords must match")
    ])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Oopsie! That username is already taken!")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Oopsie! That email is already taken!")


class NewSubfreddit(FlaskForm):
    name = StringField("Subfreddit name", validators=[InputRequired(), Length(min=3, max=28)])
    description = StringField("Description", validators=[InputRequired(), Length(min=16, max=512)])
    picture = FileField("Banner", validators=[FileAllowed(['jpg', 'png']), InputRequired()])
