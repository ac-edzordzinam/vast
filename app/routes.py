from flask import Blueprint, render_template, jsonify

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def index():
    # Sample endpoint
    return jsonify({"message": "Welcome to VAST"})

@dashboard.route('/api/cash-balance')
def cash_balance():
    # Placeholder endpoint for cash balance
    return jsonify({"cash_balance": 12000})