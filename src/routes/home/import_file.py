"""
Handles importing transactions from CSV files.
Validates file format, processes transactions and updates budgets.
"""

import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash
from werkzeug.wrappers import Response
from werkzeug.datastructures import FileStorage

from src import db
from src.utils import get_budget_by_category, add_budget_expense
from .validators import validate_file, validate_columns, process_transaction

import_bp = Blueprint('import_export', __name__)

@import_bp.route('/home-import', methods=['POST'])
def home_import() -> Response:
    """
    Handle CSV file import for transactions.

    Validates the uploaded CSV file, processes transactions and updates budget records.

    :return: A redirect to the home page.
    """
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not isinstance(file, FileStorage):
            flash('Invalid file upload!', 'danger')
            return redirect(url_for('home.home'))

        if not validate_file(file):
            return redirect(url_for('home.home'))

        with file.stream as f:
            try:
                df = pd.read_csv(f)
            except pd.errors.EmptyDataError:
                flash('CSV file is empty!', 'danger')
                return redirect(url_for('home.home'))

        if not validate_columns(df):
            return redirect(url_for('home.home'))

        for index, (_, row) in enumerate(df.iterrows()):
            transaction = process_transaction(row.to_dict(), index)
            if transaction is not None:
                budget_category = get_budget_by_category(transaction.category_id)
                add_budget_expense(budget_category, transaction.amount)

                budget_all = get_budget_by_category(0)
                add_budget_expense(budget_all, transaction.amount)

                db.session.add(transaction)

        db.session.commit()
        return redirect(url_for('home.home'))

    return redirect(url_for('home.home'))
