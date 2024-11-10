# routes/dashboard.py
from flask import Blueprint, jsonify
from services.cash_flow_service import calculate_monthly_cash_flow

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/monthly-cash-flow', methods=['GET'])
def monthly_cash_flow():
    cash_flow = calculate_monthly_cash_flow()
    return jsonify({
        'net_cash_flow': cash_flow['net'],
        'trend': cash_flow['trend']
    }), 200
