from app import db
from app.models import Transaction, Category, Budget
import requests
import os

def get_transactions():
    return [el[0] for el in db.session.execute(db.select(Transaction))]

def get_categories():
    return [el[0] for el in db.session.execute(db.select(Category))]

def get_categories_by_type(type):
    return [el[0] for el in db.session.execute(db.select(Category)
                                               .filter_by(category_type=type))]

def calculate_income():
    transactions = [el[0].amount for el in
                    db.session.execute(db.select(Transaction)
                                       .filter(Transaction.category.has(category_type='income')))]
    return sum(transactions)

def calculate_expense():
    transactions = [el[0].amount for el in
                    db.session.execute(db.select(Transaction)
                                       .filter(Transaction.category.has(category_type='expense')))]
    return sum(transactions)

def get_budget_by_category(category_id):
    return db.session.execute(
        db.select(Budget).filter_by(category_id=category_id)
    ).scalar_one_or_none()

def add_budget_expense(budget, transaction_amount):
    try:
        transaction_amount = float(transaction_amount)
    except ValueError:
        raise ValueError("Invalid transaction amount. Must be a number.")

    if budget is not None:
        budget.current_budget += transaction_amount
        # if budget.current_budget > budget.total_budget:
        #     print("Oopsie! Budget exceeded!")  # Flash emoji
        #     return

        db.session.commit()

def update_budget_expense(budget, current_amount, updated_amount):
    try:
        updated_amount = float(updated_amount)
    except ValueError:
        raise ValueError("Invalid transaction amount. Must be a number.")

    if budget is not None:
        budget.current_budget += (updated_amount - current_amount)
        db.session.commit()

def delete_budget_expense(transaction, budget):
    if budget is not None:
        # if budget.current_budget > budget.total_budget and budget.current_budget - transaction.amount < budget.total_budget:
        #     #remove emoji
        #     print("yee")

        budget.current_budget -= transaction.amount


def create_transaction(category_id, description, amount, date):
    try:
        amount = float(amount)
    except ValueError:
        raise ValueError("Invalid transaction amount.")

    new_transaction = Transaction(
        category_id=category_id,
        description=description.strip(),
        amount=amount,
        date=date
    )

    db.session.add(new_transaction)
    db.session.commit()

    return new_transaction


def get_currency_codes():
    from config import base_url
    url = f"{base_url}/codes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [code[0] for code in data["supported_codes"]]
    except requests.RequestException:
        return ["USD", "EUR", "BGN"]  # Default fallback

def get_exchange_rate(from_currency, to_currency):
    from config import base_url
    url = f"{base_url}/pair/{from_currency}/{to_currency}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('conversion_rate', 1)
    except requests.RequestException:
        return 1  # Default to 1 to prevent errors

def load_default_currency():
    if os.path.exists('currency.txt'):
        with open(os.path.join('currency.txt'), 'r') as fp:
            default_currency = fp.read()

        currency_codes = get_currency_codes()
        default_currency = default_currency if default_currency in currency_codes else 'BGN'
    else:
        default_currency = 'BGN'

    return default_currency

def save_default_currency(currency):
    with open(os.path.join('currency.txt'), 'w') as fp:
        fp.write(currency)
