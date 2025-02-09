"""
    Routes for the home page of the application.
    Handles the homepage view and displays financial data.
"""

from datetime import date

from flask import Blueprint, render_template

from src.utils import (
    calculate_income,
    calculate_expense,
    get_transactions,
    get_categories
)
from src.utils_api import get_currency_codes
from src import config

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def welcome() -> str:
    """
    Render the welcome page.

    :return: The rendered welcome page template.
    """
    return render_template('welcome.html')

@home_bp.route('/home', methods=['GET'])
def home() -> str:
    """
    Render the home page with financial data.

    Fetches income, expenses, transactions and categories, then renders the home page.

    :return: The rendered home page template.
    """
    income = calculate_income()
    expense = calculate_expense()
    transactions = get_transactions()
    categories = get_categories()
    currency_codes = get_currency_codes()

    return render_template(
        'home.html',
        transactions=transactions,
        categories=categories,
        income=income,
        expense=expense,
        date=date.today(),
        default_currency=config.DEFAULT_CURRENCY,
        currency_codes=currency_codes
    )
