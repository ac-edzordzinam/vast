import logging
from flask import Flask, g
from flask_pymongo import PyMongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize PyMongo
    # mongo.init_app(app)
    # logger.info("Initialized MongoDB connection.")

    MONGO_URI = app.config.get("MONGO_URI")
    SECRET_KEY = app.config.get("SECRET_KEY")

    # create mongo client on startup
    try:
        client = MongoClient(MONGO_URI)
        db = client.flask_db
        app.config['TRANSACTIONS_COLLECTION'] = db.transactions
        print("Connected to the database!")
    except ConnectionError as exc:
        raise RuntimeError('Failed to open database') from exc

    # Register Blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/api')
    logger.info("Registered api blueprint.")

    return app