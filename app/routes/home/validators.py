from datetime import datetime
import pandas as pd
from app import db
from ...models import Category, Transaction
from utils import get_currency_codes, get_exchange_rate
import config

def is_valid(transaction_category, transaction_amount):
    if transaction_category is None:
        #flash
        return False

    if transaction_amount == '':
        #flash
        return False

    return True

def validate_file(file):
    if not file or file.filename == '':
       # flash("No file selected!", "error")
        print("No file selected!")
        return False

    if not file.filename.endswith('.csv'):
        #flash("Invalid file format! Please upload a CSV file.", "error")
        print("Invalid file format! Please upload a CSV file.")
        return False

    return True

def validate_columns(df):
    if df.empty:
        #flash("CSV file is empty!", "error")
        print("CSV file is empty!")
        return False

    required_columns = {'date', 'category', 'description', 'amount', 'currency'}
    if not required_columns.issubset(df.columns):
        #flash(f"Invalid CSV format! Expected columns: {', '.join(required_columns)}", "error")
        print(f"Invalid CSV format! Expected columns: {', '.join(required_columns)}")
        return False

    return True

def process_transaction(row, index):
    category_name = row.get('category').strip()
    description = row.get('description')
    amount = row.get('amount')
    date_str = str(row.get('date')).strip()
    currency = row.get('currency').strip()

    category = db.session.execute(
        db.select(Category).filter_by(name=category_name)
        ).scalar_one_or_none()

    if not category:
        #flash(f"Non-existing category on row {i+1}", "error")
        print(f"Non-existing category on row {index+1}")
        return None

    description = '' if pd.isna(description) or description is None else str(description).strip()

    if not is_valid_amount(amount, index):
        return None

    amount = float(amount)

    if not is_valid_date(date_str, index):
        return None

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    amount = validate_currency(currency, amount)

    return Transaction(
        category_id=category.id,
        description=description,
        amount=amount,
        date=date_obj.strftime("%Y-%m-%d"))


def is_valid_amount(amount, i):
    if pd.isna(amount) or amount == '' or amount is None:
        #flash(f"Invalid amount on row {i+1}", "error")
        print(f"Invalid amount on row {i+1}")
        return False

    try:
        amount = float(amount)
        if amount <= 0:
            #flash(f"Invalid amount '{amount}' on row {i+1}", "error")
            print(f"Invalid amount '{amount}' on row {i+1}")
            return False
    except ValueError:
        #flash(f"Amount '{amount}' is not a valid number on row {i+1}", "error")
        print(f"Amount '{amount}' is not a valid number on row {i+1}")
        return False

    return True


def is_valid_date(date_str, i):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        #flash(f"Invalid date '{date_str}'! Expected format: YYYY-MM-DD on row {i+1}", "error")
        print(f"Invalid date '{date_str}'! Expected format: YYYY-MM-DD on row {i+1}")
        return False

    return True

def validate_currency(currency, amount):
    currency_codes = get_currency_codes()
    if currency not in currency_codes:
        currency = 'BGN'
    elif currency != config.default_currency:
        exchange_rate = get_exchange_rate(currency, config.default_currency)
        amount *= exchange_rate

    return amount
