from flask import Blueprint, request, jsonify, redirect, flash, abort, current_app
# from .models import db
from bson.objectid import ObjectId
from bson.errors import InvalidId
import logging
from datetime import datetime

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
    
@api.route('/transactions_by_month', methods=['POST'])
def get_transactions_by_month():
    try:
        user_id = request.args.get('user_id')
        month = request.args.get('month')
        year = request.args.get('year')
        category = request.args.get('category')

        if not user_id or not month or not year:
            return jsonify({"error": "Missing required parameters: user_id, month, or year"}), 400

        try:
            # Parse start and end dates based on month and year
            start_date = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
            if int(month) == 12:  # Handling December edge case
                end_date = datetime.strptime(f"{int(year) + 1}-01-01", "%Y-%m-%d")
            else:
                end_date = datetime.strptime(f"{year}-{int(month) + 1}-01", "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format for year or month"}), 400

        # Log the parsed dates
        print(f"Start Date: {start_date}, End Date: {end_date}")

        # Build MongoDB query - no need for ISODate conversion, just pass datetime objects
        query = {
            "user_id": user_id,
            "date": {"$gte": start_date, "$lt": end_date}
        }
        if category:
            query["category"] = category

        print("Query being sent to MongoDB:", query)

        # Query the database
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        filtered_transactions = transactions_table.find(query)

        # Prepare the list of transactions
        transactions_list = []
        for transaction in filtered_transactions:
            transaction['_id'] = str(transaction['_id'])  # Convert ObjectId to string
            transactions_list.append(transaction)

        print("Filtered Transactions:", transactions_list)  # Log the transactions

        # If no transactions, return empty array
        return jsonify(transactions_list if transactions_list else [])

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@api.route('/transactions_by_category', methods=['POST'])
def get_transactions_by_category():
    try:
        user_id = request.args.get('user_id')
        category = request.args.get('category')

        if not user_id or not category:
            return jsonify({"error": "Missing required parameters: user_id or category"}), 400

        # Log the parameters being used
        print(f"Filtering transactions for user_id: {user_id}, category: {category}")

        # Build MongoDB query to filter by user_id and category
        query = {
            "user_id": user_id,
            "category": category
        }

        print("Query being sent to MongoDB:", query)

        # Query the database
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        filtered_transactions = transactions_table.find(query)

        # Prepare the list of transactions
        transactions_list = []
        for transaction in filtered_transactions:
            transaction['_id'] = str(transaction['_id'])  # Convert ObjectId to string
            transactions_list.append(transaction)

        print("Filtered Transactions:", transactions_list)  # Log the transactions

        # If no transactions, return empty array
        return jsonify(transactions_list if transactions_list else [])

    except Exception as e:
        return jsonify({"error": str(e)}), 500





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