from datetime import date
from flask import Blueprint, render_template
from .transactions import calculate_income, calculate_expense, get_transactions, get_categories
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

    return render_template('home.html', transactions=transactions, categories=categories,
                           income=income, expense=expense, date=date.today())
