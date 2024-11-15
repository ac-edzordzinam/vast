from flask import g, current_app
from bson import ObjectId
from flask_pymongo import PyMongo
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from config import mongo

# Initialize db
db = mongo.db

def add_transaction(user_id, amount, category, transaction_type, date):
    transaction = {
        'user_id': user_id,
        'amount': amount,
        'category': category,
        'transaction_type': transaction_type,
        'date': date
    }
    return db.transactions.insert_one(transaction)

def get_transaction(transaction_id):
    return db.transactions.find_one({"_id": ObjectId(transaction_id)})

def update_transaction(transaction_id, data):
    return db.transactions.update_one(
        {"_id": ObjectId(transaction_id)}, 
        {"$set": data}
    )

def delete_transaction(transaction_id):
    return db.transactions.delete_one({"_id": ObjectId(transaction_id)})

def get_transactions_by_user(user_id):
    return list(db.transactions.find({"user_id": user_id}))
