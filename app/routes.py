from flask import Blueprint, request, jsonify, redirect, flash, abort, current_app
# from .models import db
from bson.objectid import ObjectId
from bson.errors import InvalidId
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/status')
def status():
    logger.info("Accessed status route.")
    return jsonify({"message": "Welcome to VAST"})



# render the home page
@api.route('/all_transactions')
def get_all_transactions():
    transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
    all_transactions = transactions_table.find() 
    transactions_list = []
    for transaction in all_transactions:
        transaction['_id'] = str(transaction['_id'])  # Convert ObjectId to string for JSON serialization
        transactions_list.append(transaction)

    # Return the list as JSON
    return jsonify(transactions_list)
    


# add item to the list
@api.route("/create", methods=["POST"])
def create():
    transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
    try:
        data = request.get_json()
        user_id = data["user_id"]
        amount = float(data["amount"])
        category = data["category"]
        transaction_type = data["transaction_type"]
        date = data["date"]

        transaction = {
            'user_id': user_id,
            'amount': amount,
            'category': category,
            'transaction_type': transaction_type,
            'date': date
        }

        if transactions_table.insert_one(transaction):
            logger.info(f"Inserted document: {transaction}")
            return jsonify({"message": "Transaction added successfully!"}), 201
        else:
            return jsonify({"message": "Error adding transaction"}), 500
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        return jsonify({"message": "Error adding transaction"}), 500


# update an existing item
@api.route("/update", methods=["POST"])
def update():
    transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
    try:
        data = request.get_json()
        transaction_id = data["transaction_id"]
        new_data = {
            'user_id': data["user_id"],
            'amount': float(data["amount"]),
            'category': data["category"],
            'transaction_type': data["transaction_type"],
            'date': data["date"]
        }

        document_to_update = {'_id': ObjectId(transaction_id)}
        update_document = {'$set': new_data}

        if transactions_table.find_one(document_to_update) is None:
            logger.warning("No document found with that ID")
            return jsonify({"message": "No document found with that ID"}), 404
        else:
            transactions_table.update_one(document_to_update, update_document)
            return jsonify({"message": "Transaction updated successfully!"}), 200
    except InvalidId:
        logger.error("Invalid transaction ID")
        return jsonify({"message": "Invalid transaction ID"}), 400
    except Exception as e:
        logger.error(f"Error updating transaction: {e}")
        return jsonify({"message": "Error updating transaction"}), 500


# delete an item
@api.route("/delete", methods=["POST"])
def delete():
    transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
    try:
        data = request.get_json()
        transaction_id = data["transaction_id"]
        document_to_delete = {'_id': ObjectId(transaction_id)}

        if transactions_table.find_one(document_to_delete) is None:
            logger.warning("No document found with that ID")
            return jsonify({"message": "No document found with that ID"}), 404
        else:
            transactions_table.delete_one(document_to_delete)
            logger.info(f"Deleted document with ID: {transaction_id}")
            return jsonify({"message": "Transaction deleted successfully!"}), 200
    except InvalidId:
        logger.error("Invalid transaction ID")
        return jsonify({"message": "Invalid transaction ID"}), 400
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        return jsonify({"message": "Error deleting transaction"}), 500