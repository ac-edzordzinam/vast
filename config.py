import os

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    MONGO_URI = os.environ.get('CONNECTION_STRING')

