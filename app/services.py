from app.models import get_transactions_by_user
from datetime import datetime

def calculate_monthly_net_cash_flow(user_id, month=None):
    if not month:
        month = datetime.now().month
    
    transactions = get_transactions_by_user(user_id)
    
    income = 0
    expense = 0
    for transaction in transactions:
        transaction_month = datetime.strptime(transaction['date'], '%Y-%m-%d').month
        if transaction_month == month:
            if transaction['transaction_type'] == 'income':
                income += transaction['amount']
            elif transaction['transaction_type'] == 'expense':
                expense += transaction['amount']

    return income - expense

def calculate_top_expenses(user_id, limit=3):
    transactions = get_transactions_by_user(user_id)
    expenses = {}
    
    for transaction in transactions:
        if transaction['transaction_type'] == 'expense':
            category = transaction['category']
            if category not in expenses:
                expenses[category] = 0
            expenses[category] += transaction['amount']
    
    # Sort and get top N categories
    sorted_expenses = sorted(expenses.items(), key=lambda x: x[1], reverse=True)
    return sorted_expenses[:limit]