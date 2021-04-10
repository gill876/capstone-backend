from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from .config import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

auth = HTTPBasicAuth(scheme='Bearer')

from app import views
