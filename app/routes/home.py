from flask import render_template, Blueprint
from datetime import date

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def welcome():
    return render_template('welcome.html')

@home_bp.route('/home')
def home():
    transactions = [
        {'date': '2024-12-29', 'category': 'Food', 'description': 'Lunch at restaurant', 'amount': -15.00},
        {'date': '2024-12-28', 'category': 'Salary', 'description': 'Monthly salary', 'amount': 2000.00},
    ]
    income = calculate_income()
    return render_template('home.html', transactions=transactions, income=income, date=date.today())

def calculate_income():
    return 0