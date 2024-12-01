from flask import Blueprint, request, jsonify, redirect, flash, abort, current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
import logging
from datetime import datetime, timedelta
from bson.son import SON

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/status', methods=['GET'])
def status():
    logger.info("Accessed status route.")
    return jsonify({"message": "Welcome to VAST"})


# Get all transactions (GET is fine here for retrieving all data)
@api.route('/transactions/all', methods=['GET'])
def get_all_transactions():
    transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
    all_transactions = transactions_table.find() 
    transactions_list = []
    for transaction in all_transactions:
        transaction['_id'] = str(transaction['_id'])  # Convert ObjectId to string for JSON serialization
        transactions_list.append(transaction)

    return jsonify(transactions_list)


# Refactor the transactions filter for month to use POST
@api.route('/transactions/filter/month', methods=['POST'])
def get_transactions_by_month():
    try:
        # Getting JSON data from the request body (POST request)
        data = request.get_json()
        user_id = data.get('user_id')
        month = data.get('month')
        year = data.get('year')
        category = data.get('category')
        transaction_type = data.get('transaction_type')

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

        # Build MongoDB query
        query = {
            "user_id": user_id,
            "date": {"$gte": start_date, "$lt": end_date}
        }
        if category:
            query["category"] = category
        if transaction_type:
            query["transaction_type"] = transaction_type  # Apply transaction_type filter

        # Query the database and aggregate to calculate the sum
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_amount": {"$sum": "$amount"}
            }}
        ]

        result = transactions_table.aggregate(pipeline)
        total_amount = 0
        for item in result:
            total_amount = item.get('total_amount', 0)

        # Query for individual transactions
        filtered_transactions = transactions_table.find(query)
        transactions_list = []
        for transaction in filtered_transactions:
            transaction['_id'] = str(transaction['_id'])
            transactions_list.append(transaction)

        response_data = {
            "transactions": transactions_list if transactions_list else [],
            "total_amount": total_amount
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Refactor transactions by category to use POST (as it's filtering based on a body request)
@api.route('/transactions/filter/category', methods=['POST'])
def get_transactions_by_category():
    try:
        # Getting JSON data from the request body
        data = request.get_json()
        user_id = data.get('user_id')
        category = data.get('category')

        if not user_id or not category:
            return jsonify({"error": "Missing required parameters: user_id or category"}), 400

        query = {
            "user_id": user_id,
            "category": category
        }

        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        filtered_transactions = transactions_table.find(query)

        transactions_list = []
        for transaction in filtered_transactions:
            transaction['_id'] = str(transaction['_id'])  # Convert ObjectId to string
            transactions_list.append(transaction)

        return jsonify(transactions_list if transactions_list else [])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create a new transaction (POST is correct here, as it creates a resource)
@api.route("/transactions/create", methods=["POST"])
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


# Update an existing transaction (POST is used to update a resource)
@api.route("/transactions/update", methods=["POST"])
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


# Delete a transaction (POST is used for deletion here as well, to avoid GET method issues)
@api.route("/transactions/delete", methods=["POST"])
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




@api.route('/transactions/net_cash_flow', methods=['POST'])
def get_monthly_net_cash_flow():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        year = data.get('year')

        if not user_id or not year:
            return jsonify({"error": "Missing required parameters: user_id or year"}), 400

        # MongoDB pipeline to group by month and calculate total revenue and expenses
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {
                        "$gte": datetime.strptime(f"{year}-01-01", "%Y-%m-%d"),
                        "$lt": datetime.strptime(f"{int(year) + 1}-01-01", "%Y-%m-%d")
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "month": {"$month": "$date"},
                        "year": {"$year": "$date"}
                    },
                    "total_income": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Income"]}, "$amount", 0]}
                    },
                    "total_expenses": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Expense"]}, "$amount", 0]}
                    }
                }
            },
            {
                "$sort": {"_id.month": 1}  # Sort by month
            }
        ]

        # Query the database with aggregation
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        result = transactions_table.aggregate(pipeline)

        # Month names mapping
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }

        # Format the results
        monthly_data = []
        for item in result:
            month = item['_id']['month']
            total_income = item['total_income']
            total_expenses = item['total_expenses']
            net_cash_flow = total_income - total_expenses

            monthly_data.append({
                "month": month_names.get(month),
                "revenue": total_income,
                "expenses": total_expenses,
                "netCashFlow": net_cash_flow
            })

        # Ensure all months (Jan to Dec) are represented
        all_months = {month_names[i]: {"revenue": 0, "expenses": 0, "netCashFlow": 0} for i in range(1, 13)}

        for data in monthly_data:
            all_months[data["month"]] = data

        # Return the aggregated data in the desired format
        return jsonify({
            "monthlyNetCashFlow": {
                "title": "Monthly Net Cash Flow",
                "data": list(all_months.values())
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@api.route('/transactions/revenue_trends', methods=['GET'])
def get_revenue_trends():
    try:
        # Get the current date and calculate the previous week's start and end dates (Sunday to Saturday)
        today = datetime.today()
        start_of_previous_week = today - timedelta(days=today.weekday() + 7)  # Subtract 7 days to get the previous week
        end_of_previous_week = start_of_previous_week + timedelta(days=6)  # Saturday of the previous week

        # Remove the time part of the date (only compare the date)
        start_of_previous_week = start_of_previous_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_previous_week = end_of_previous_week.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Debugging: Print the date range to check
        print(f"Start of previous week: {start_of_previous_week}")
        print(f"End of previous week: {end_of_previous_week}")

        # MongoDB pipeline to get transactions for the previous week
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_of_previous_week,
                        "$lte": end_of_previous_week
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "day_of_week": {"$dayOfWeek": "$date"}  # 1 = Sunday, 2 = Monday, ..., 7 = Saturday
                    },
                    "total_income": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Income"]}, "$amount", 0]}
                    },
                    "total_expenses": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Expense"]}, "$amount", 0]}
                    }
                }
            },
            {
                "$sort": {"_id.day_of_week": 1}  # Sort by day of the week (1 = Sunday, 7 = Saturday)
            }
        ]

        # Query the database with aggregation
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        result = transactions_table.aggregate(pipeline)

        # Weekday names mapping
        weekday_names = {
            1: "Sun", 2: "Mon", 3: "Tue", 4: "Wed", 5: "Thu", 6: "Fri", 7: "Sat"
        }

        # Format the results
        weekly_data = []
        for item in result:
            day_of_week = item['_id']['day_of_week']
            total_income = item['total_income']
            total_expenses = item['total_expenses']

            weekly_data.append({
                "day": weekday_names.get(day_of_week),
                "revenue": total_income,
                "expenses": total_expenses
            })

        # Ensure all days of the week (Sun-Sat) are represented
        all_days_of_week = {weekday_names[i]: {"revenue": 0, "expenses": 0} for i in range(1, 8)}

        # Fill in the actual data
        for data in weekly_data:
            all_days_of_week[data["day"]] = data

        # Return the aggregated data in the desired format
        return jsonify({
            "revenueTrends": {
                "title": "Revenue and Expense Trend (Previous Week)",
                "data": list(all_days_of_week.values())
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    




@api.route('/transactions/top_expenses', methods=['POST'])
def get_top_expenses():
    try:
        # Get the year from the request body
        data = request.get_json()
        year = data.get('year')

        if not year:
            return jsonify({"error": "Missing required parameter: year"}), 400

        # Ensure year is a valid integer
        try:
            year = int(year)
        except ValueError:
            return jsonify({"error": "Invalid year format"}), 400

        # Calculate the start and end dates for the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        # MongoDB pipeline to aggregate expenses by category
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lt": end_date
                    },
                    "transaction_type": "Expense"  # Only consider expenses
                }
            },
            {
                "$group": {
                    "_id": "$category",  # Group by category
                    "total_expenses": {"$sum": "$amount"}
                }
            },
            {
                "$sort": SON([("total_expenses", -1)])  # Sort by total_expenses in descending order
            },
            {
                "$limit": 3  # Only take the top 3 categories
            }
        ]

        # Query the database using the aggregation pipeline
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        result = transactions_table.aggregate(pipeline)

        # Format the response data
        top_expenses = []
        for item in result:
            top_expenses.append({
                "name": item["_id"],  # Category name
                "amount": item["total_expenses"]  # Total expense amount for the category
            })

        # Return the data in the required format
        return jsonify({
            "topExpense": {
                "category": "Expenses",
                "title": "Top 3 Expenses",
                "data": top_expenses
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@api.route('/transactions/financial_summary', methods=['POST'])
def get_financial_summary():
    try:
        # Get the year from the request body
        data = request.get_json()
        user_id = data.get('user_id')
        year = data.get('year')

        if not user_id or not year:
            return jsonify({"error": "Missing required parameters: user_id or year"}), 400

        # MongoDB aggregation for monthly net cash flow
        pipeline_monthly_net_cash_flow = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {
                        "$gte": datetime.strptime(f"{year}-01-01", "%Y-%m-%d"),
                        "$lt": datetime.strptime(f"{int(year) + 1}-01-01", "%Y-%m-%d")
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "month": {"$month": "$date"},
                        "year": {"$year": "$date"}
                    },
                    "total_income": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Income"]}, "$amount", 0]}
                    },
                    "total_expenses": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Expense"]}, "$amount", 0]}
                    }
                }
            },
            {
                "$sort": {"_id.month": 1}
            }
        ]

        # MongoDB aggregation for revenue trends (previous week)
        today = datetime.today()
        start_of_previous_week = today - timedelta(days=today.weekday() + 7)  # Subtract 7 days to get the previous week
        end_of_previous_week = start_of_previous_week + timedelta(days=6)  # Saturday of the previous week

        # Remove the time part of the date (only compare the date)
        start_of_previous_week = start_of_previous_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_previous_week = end_of_previous_week.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Debugging: Print the date range to check
        print(f"Start of previous week: {start_of_previous_week}")
        print(f"End of previous week: {end_of_previous_week}")

        # MongoDB pipeline to get transactions for the previous week
        pipeline_revenue_trends = [
            {
                "$match": {
                    "date": {
                        "$gte": start_of_previous_week,
                        "$lte": end_of_previous_week
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "day_of_week": {"$dayOfWeek": "$date"}  # 1 = Sunday, 2 = Monday, ..., 7 = Saturday
                    },
                    "total_income": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Income"]}, "$amount", 0]}
                    },
                    "total_expenses": {
                        "$sum": {"$cond": [{"$eq": ["$transaction_type", "Expense"]}, "$amount", 0]}
                    }
                }
            },
            {
                "$sort": {"_id.day_of_week": 1}  # Sort by day of the week (1 = Sunday, 7 = Saturday)
            }
        ]

        # MongoDB aggregation for top 3 expenses
        pipeline_top_expenses = [
            {
                "$match": {
                    "date": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    },
                    "transaction_type": "Expense"
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total_expenses": {"$sum": "$amount"}
                }
            },
            {
                "$sort": SON([("total_expenses", -1)])
            },
            {
                "$limit": 3
            }
        ]

        # Query the database with aggregation for monthly net cash flow
        transactions_table = current_app.config['TRANSACTIONS_COLLECTION']
        result_monthly_net_cash_flow = transactions_table.aggregate(pipeline_monthly_net_cash_flow)
        
        # Query the database with aggregation for revenue trends (previous week)
        result_revenue_trends = transactions_table.aggregate(pipeline_revenue_trends)
        
        # Query the database with aggregation for top expenses
        result_top_expenses = transactions_table.aggregate(pipeline_top_expenses)

        # Month names and weekday names mapping
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        weekday_names = {
            1: "Sun", 2: "Mon", 3: "Tue", 4: "Wed", 5: "Thu", 6: "Fri", 7: "Sat"
        }

        # Prepare monthly net cash flow data
        monthly_data = []
        for item in result_monthly_net_cash_flow:
            month = item['_id']['month']
            total_income = item['total_income']
            total_expenses = item['total_expenses']
            net_cash_flow = total_income - total_expenses

            monthly_data.append({
                "month": month_names.get(month),
                "revenue": total_income,
                "expenses": total_expenses,
                "netCashFlow": net_cash_flow
            })

        # Ensure all months (Jan to Dec) are represented
        all_months = {month_names[i]: {"revenue": 0, "expenses": 0, "netCashFlow": 0} for i in range(1, 13)}
        for data in monthly_data:
            all_months[data["month"]] = data

        # Prepare revenue trends data
        weekly_data = []
        for item in result_revenue_trends:
            day_of_week = item['_id']['day_of_week']
            total_income = item['total_income']
            total_expenses = item['total_expenses']

            weekly_data.append({
                "day": weekday_names.get(day_of_week),
                "revenue": total_income,
                "expenses": total_expenses
            })

        # Ensure all days of the week (Sun-Sat) are represented
        all_days_of_week = {weekday_names[i]: {"revenue": 0, "expenses": 0} for i in range(1, 8)}
        for data in weekly_data:
            all_days_of_week[data["day"]] = data

        # Prepare top expenses data
        top_expenses = []
        for item in result_top_expenses:
            top_expenses.append({
                "name": item["_id"],
                "amount": item["total_expenses"]
            })

        # Prepare financial cards (mocked as an example)
        expense_cards = [
            {"id": "1", "title": "Current Cash Balance", "amount": "GHC 25,000"},
            {"id": "2", "title": "Total Income", "amount": "GHC 10,000"},
            {"id": "3", "title": "Bonus Generated", "amount": "GHC 50,000"},
            {"id": "4", "title": "Paid Amount", "amount": "GHC 3,000"},
            {"id": "5", "title": "Pending Amount", "amount": "GHC 100,000"}
        ]

        # Prepare financial tips (mocked as an example)
        financial_tips = [
            {"id": "1", "title": "Current Cash Balance", "description": "Ensure you have at least 3 months’ worth of expenses saved for emergencies."},
            {"id": "2", "title": "Total Income", "description": "Evaluate your income streams and look for opportunities to increase them."},
            {"id": "3", "title": "Bonus Generated", "description": "Use your bonus wisely: save or invest for long-term financial security."},
            {"id": "4", "title": "Paid Amount", "description": "Track paid amounts closely to stay within your budget and avoid over-spending."},
            {"id": "5", "title": "Pending Amount", "description": "Pay pending bills on time to maintain a healthy credit score."}
        ]

        # Return the aggregated data in the desired format
        return jsonify({
            "expenseCards": expense_cards,
            "monthlyNetCashFlow": {
                "title": "Monthly Net Cash Flow",
                "data": list(all_months.values())
            },
            "revenueTrends": {
                "title": "Revenue and Expense Trend",
                "data": list(all_days_of_week.values())
            },
            "financialTip": financial_tips,
            "topExpense": {
                "category": "Expenses",
                "title": "Top 3 Expenses",
                "data": top_expenses
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500