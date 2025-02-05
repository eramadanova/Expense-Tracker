from datetime import date
from flask import Blueprint, render_template
from utils import calculate_income, calculate_expense, get_transactions, get_categories, get_currency_codes
import config

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def welcome():
    return render_template('welcome.html')

@home_bp.route('/home', methods=['GET'])
def home():
    income = calculate_income()
    expense = calculate_expense()
    transactions = get_transactions()
    categories = get_categories()
    currency_codes = get_currency_codes()

    return render_template('home.html', transactions=transactions, categories=categories,
                           income=income, expense=expense,
                           date=date.today(), default_currency=config.default_currency,
                           currency_codes=currency_codes)
