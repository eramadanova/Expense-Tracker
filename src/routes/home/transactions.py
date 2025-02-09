"""
Handles transaction operations such as creation, updating and deletion.
"""

from flask import Blueprint, request, redirect, url_for, flash
from werkzeug.wrappers import Response

from src.utils import (
    get_budget_by_category,
    add_budget_expense,
    create_transaction,
    update_budget_expense,
    delete_budget_expense,
    get_transaction_by_id
)
from src import db
from .validators import is_valid, validate_currency

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/home-transaction', methods=['POST'])
def home_transaction() -> Response:
    """
    Handles the creation of a new transaction.

    Retrieves transaction details from the form, validates inputs,
    updates the budget and creates a new transaction record.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        transaction_date = request.form['transaction_date'].strip()
        transaction_category = request.form['transaction_category'].strip()
        transaction_amount = request.form['transaction_amount'].strip()
        transaction_description = request.form['transaction_description'].strip()
        transaction_currency = request.form['transaction_currency'].strip()

        if not is_valid(transaction_category, transaction_amount):
            return redirect(url_for('home.home'))

        transaction_amount_num = validate_currency(transaction_currency, float(transaction_amount))

        budget_category = get_budget_by_category(int(transaction_category))
        add_budget_expense(budget_category, transaction_amount_num)

        budget_all = get_budget_by_category(0)
        add_budget_expense(budget_all, transaction_amount_num)

        create_transaction(int(transaction_category),
                            transaction_description,
                            transaction_amount_num,
                            transaction_date)

        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))


@transactions_bp.route('/home-update', methods=['POST'])
def home_update() -> Response:
    """
    Handles updating an existing transaction.

    Retrieves transaction details from the form, validates inputs,
    updates the associated budget and modifies the transaction record.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        transaction_id = request.form['transaction_id'].strip()
        updated_category = request.form['transaction_category'].strip()
        updated_description = request.form['transaction_description'].strip()
        updated_amount = request.form['transaction_amount'].strip()
        updated_date = request.form['transaction_date'].strip()
        updated_currency = request.form['transaction_currency'].strip()

        transaction = get_transaction_by_id(int(transaction_id))

        if not transaction or not is_valid(updated_category, updated_amount):
            flash('Transaction not found.', 'error')
            return redirect(url_for('home.home'))

        updated_amount_float = validate_currency(updated_currency, float(updated_amount))

        budget_category = get_budget_by_category(int(updated_category))
        update_budget_expense(budget_category, transaction.amount, updated_amount_float)

        budget_all = get_budget_by_category(0)
        update_budget_expense(budget_all, transaction.amount, updated_amount_float)

        transaction.category_id = int(updated_category)
        transaction.description = updated_description
        transaction.amount = updated_amount_float
        transaction.date = updated_date

        db.session.commit()
        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))


@transactions_bp.route('/home-delete', methods=['POST'])
def home_delete() -> Response:
    """
    Handles the deletion of a transaction.

    Retrieves the transaction ID from the form, updates the budget
    and deletes the transaction record from the database.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        transaction_id = request.form['transaction_id'].strip()

        transaction = get_transaction_by_id(int(transaction_id))

        if transaction is None:
            flash('Transaction not found.', 'error')
            return redirect(url_for('home.home'))

        budget_category = get_budget_by_category(transaction.category_id)
        delete_budget_expense(transaction, budget_category)

        budget_all = get_budget_by_category(0)
        delete_budget_expense(transaction, budget_all)

        db.session.delete(transaction)
        db.session.commit()

        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))
