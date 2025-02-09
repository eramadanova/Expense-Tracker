"""
Handles transaction operations such as creation, updating and deletion.
"""

from flask import Blueprint, request, redirect, url_for, flash, Response
from typing import Union
from werkzeug.wrappers import Response as WerkzeugResponse

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
def home_transaction() -> Union[Response, WerkzeugResponse]:
    """
    Handles the creation of a new transaction.

    Retrieves transaction details from the form, validates inputs,
    updates the budget and creates a new transaction record.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        transaction_date = request.form.get('transaction_date')
        transaction_category = request.form.get('transaction_category')
        transaction_amount = request.form.get('transaction_amount')
        transaction_description = request.form.get('transaction_description').strip()
        transaction_currency = request.form.get('transaction_currency')

        if not is_valid(transaction_category, transaction_amount):
            return redirect(url_for('home.home'))

        transaction_amount = validate_currency(transaction_currency, transaction_amount)

        budget_category = get_budget_by_category(transaction_category)
        add_budget_expense(budget_category, transaction_amount)

        budget_all = get_budget_by_category(0)
        add_budget_expense(budget_all, transaction_amount)

        create_transaction(transaction_category,
                            transaction_description,
                            transaction_amount,
                            transaction_date)

        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))


@transactions_bp.route('/home-update', methods=['POST'])
def home_update() -> Union[Response, WerkzeugResponse]:
    """
    Handles updating an existing transaction.

    Retrieves transaction details from the form, validates inputs,
    updates the associated budget and modifies the transaction record.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        updated_category = request.form.get('transaction_category')
        updated_description = request.form.get('transaction_description').strip()
        updated_amount = request.form.get('transaction_amount')
        updated_date = request.form.get('transaction_date')
        updated_currency = request.form.get('transaction_currency')

        transaction = get_transaction_by_id(transaction_id)

        if not transaction or not is_valid(updated_category, updated_amount):
            flash('Transaction not found.', 'error')
            return redirect(url_for('home.home'))

        updated_amount = validate_currency(updated_currency, float(updated_amount))

        budget_category = get_budget_by_category(updated_category)
        update_budget_expense(budget_category, transaction.amount, updated_amount)

        budget_all = get_budget_by_category(0)
        update_budget_expense(budget_all, transaction.amount, updated_amount)

        transaction.category_id = updated_category
        transaction.description = updated_description
        transaction.amount = updated_amount
        transaction.date = updated_date

        db.session.commit()
        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))


@transactions_bp.route('/home-delete', methods=['POST'])
def home_delete() -> Union[Response, WerkzeugResponse]:
    """
    Handles the deletion of a transaction.

    Retrieves the transaction ID from the form, updates the budget
    and deletes the transaction record from the database.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')

        transaction = get_transaction_by_id(transaction_id)

        budget_category = get_budget_by_category(transaction.category_id)
        delete_budget_expense(transaction, budget_category)

        budget_all = get_budget_by_category(0)
        delete_budget_expense(transaction, budget_all)

        db.session.delete(transaction)
        db.session.commit()

        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))
