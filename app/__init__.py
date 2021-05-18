from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from .config import Config
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


CORS(app)
# app.config["CORS_HEADERS"] = "Content-Type"

app.config.from_object(Config)

db = SQLAlchemy(app)

auth = HTTPBasicAuth(scheme='Bearer')

from app import views
