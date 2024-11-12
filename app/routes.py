from flask import Blueprint, jsonify
from app.models import add_transaction, get_transaction, update_transaction, delete_transaction, get_transactions_by_user


dashboard_bp = Blueprint('dashboard', __name__)
@dashboard_bp.route('/')
def index():
    # Sample endpoint
    return jsonify({"message": "Welcome to VAST"})

@dashboard_bp.route('/api/cash-balance')
def cash_balance():
    # Placeholder endpoint for cash balance
    return jsonify({"cash_balance": 12000})



@dashboard_bp.route('/add_transaction', methods=['POST'])
def add_transaction_route():
    data = request.json
    transaction = add_transaction(
        data['user_id'], data['amount'], data['category'], data['transaction_type'], data['date']
    )
    return jsonify({"success": True, "inserted_id": str(transaction.inserted_id)})

@dashboard_bp.route('/get_transaction/<transaction_id>', methods=['GET'])
def get_transaction_route(transaction_id):
    transaction = get_transaction(transaction_id)
    if transaction:
        return jsonify(transaction), 200
    return jsonify({"error": "Transaction not found"}), 404

@dashboard_bp.route('/update_transaction/<transaction_id>', methods=['PUT'])
def update_transaction_route(transaction_id):
    data = request.json
    updated = update_transaction(transaction_id, data)
    if updated.modified_count > 0:
        return jsonify({"success": True})
    return jsonify({"error": "Update failed"}), 404

@dashboard_bp.route('/delete_transaction/<transaction_id>', methods=['DELETE'])
def delete_transaction_route(transaction_id):
    result = delete_transaction(transaction_id)
    if result.deleted_count > 0:
        return jsonify({"success": True})
    return jsonify({"error": "Transaction not found"}), 404

@dashboard_bp.route('/get_transactions_by_user/<user_id>', methods=['GET'])
def get_transactions_by_user_route(user_id):
    transactions = get_transactions_by_user(user_id)
    return jsonify(transactions)