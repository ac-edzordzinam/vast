from flask_pymongo import PyMongo
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


app.config["MONGO_URI"]=os.getenv('CONNECTION_STRING') 
mongo = PyMongo(app)
db= mongo.db