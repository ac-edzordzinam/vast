# services/cash_flow_service.py
from models.transaction import Transaction
from datetime import datetime

def calculate_monthly_cash_flow():
    month_start = datetime(datetime.now().year, datetime.now().month, 1)
    transactions = Transaction.query.filter(Transaction.date >= month_start)
    
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    net_cash_flow = income - expenses
    
    return {
        'net': net_cash_flow,
        'trend': 'positive' if net_cash_flow > 0 else 'negative'
    }