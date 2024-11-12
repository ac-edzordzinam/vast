from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    
    # Initialize Flask-PyMongo with the Flask app
    mongo.init_app(app)
 # Register Blueprints here if needed
    from .routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app
   