import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi 
from app.routes import dashboard
from config import app
from flask import Flask


load_dotenv()  # Load environment variables from .env file


def create_app():
    app = Flask(__name__)
    app.register_blueprint(dashboard)
    app.config.from_object(Config)

    # Initialize MongoDB client
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.db = mongo_client.get_database()  # Set the default database

    # Register blueprints here
    #app.register_blueprint(dashboard, url_prefix='/dashboard')

    return app

if __name__ == "__main__":
    app.run()