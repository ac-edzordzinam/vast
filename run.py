from app import create_app
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi



if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True
    app.config['MONGO_URI']

    app.run()