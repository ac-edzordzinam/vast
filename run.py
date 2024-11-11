from app import create_app
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi


load_dotenv()
uri = os.environ.get('CONNECTION_STRING')
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
    
    app = create_app()

if __name__ == "__main__":
    app.run(debug=True)