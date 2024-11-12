import os
class Config:
    DEBUG = True
    SECRET_KEY = 'supersecretkey'

    MONGO_URI = os.getenv('CONNECTION_STRING')  