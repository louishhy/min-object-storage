from flask import Flask
from .routes import users_bp, data_bp
from .config import DefaultConfig
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

def create_app(config_class=DefaultConfig):
    load_dotenv()
    # 1. Create app
    app = Flask(__name__)
    # 2. Config app from object
    app.config.from_object(config_class)
    # 3. Register w/ blueprint
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(data_bp, url_prefix="/data")

    return app