from datetime import date
from flask import render_template, Blueprint, request, redirect, url_for
from .. import db
from ..models import Category, Transaction

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def welcome():
    return render_template('welcome.html')

@home_bp.route('/home', methods=['GET'])
def home():
    income = calculate_income()
    expense = calculate_expense()
    transactions  = [el[0] for el in db.session.execute(db.select(Transaction))]
    categories = [el[0] for el in db.session.execute(db.select(Category))]

    return render_template('home.html', transactions=transactions, categories=categories,
                           income=income, expense=expense, date=date.today())

@home_bp.route('/home-transaction', methods=['POST'])
def home_transaction():
    if request.method == 'POST':
        transaction_date = request.form.get('transaction_date')
        transaction_category = request.form.get('transaction_category')
        transaction_amount = request.form.get('transaction_amount')
        transaction_description = request.form.get('transaction_description').strip()
        transaction_currency = request.form.get('transaction_currency')

        if not is_valid(transaction_category, transaction_amount, transaction_currency):
            return redirect(url_for('home.home'))

        new_transaction = Transaction(
            category_id=transaction_category,
            description=transaction_description,
            amount=float(transaction_amount),
            date=transaction_date)
        db.session.add(new_transaction)
        db.session.commit()
        #flash("Transaction added successfully!", "success")
        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))

def is_valid(transaction_category, transaction_amount, transaction_currency):
    #check if currency is equal to default currency -> if not use API to convert it to database

    if transaction_category is None:
        #flash
        return False

    if transaction_amount == '':
        #flash
        return False

    return True

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

@home_bp.route('/home-update', methods=['POST'])
def home_update():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        updated_category = request.form.get('transaction_category')
        updated_description = request.form.get('transaction_description').strip()
        updated_amount = request.form.get('transaction_amount')
        updated_date = request.form.get('transaction_date')
        updated_currency = request.form.get('transaction_currency')

        # Намери транзакцията
        transaction = db.session.execute(
                      db.select(Transaction).filter_by(id=transaction_id)
                      ).scalar_one_or_none()

        if not is_valid(updated_category, updated_amount, updated_currency):
            return redirect(url_for('home.home'))

        if transaction is None:
            #flash("Transaction not found.", "error")
            return redirect(url_for('transactions_page'))

        # Обнови стойностите
        transaction.category_id = updated_category
        transaction.description = updated_description
        transaction.amount = float(updated_amount)
        transaction.date = updated_date

        # Запази промените
        db.session.commit()

        #flash("Transaction updated successfully!", "success")
        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))

@home_bp.route('/home-delete', methods=['POST'])
def home_delete():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')

        db.session.query(Transaction).filter_by(id=transaction_id).delete()
        db.session.commit()
        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))
