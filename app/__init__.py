from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app)

app.config.from_object(Config)

db = SQLAlchemy(app)

from app import views
