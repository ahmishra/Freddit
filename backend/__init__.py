import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

app = Flask(__name__,  template_folder='../frontend/html', static_folder="../frontend/styles")
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

from backend.models import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 

from backend import routes
