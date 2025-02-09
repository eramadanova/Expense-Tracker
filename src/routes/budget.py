"""
    Defines budget-related routes for the Flask application.
"""

from flask import render_template, Blueprint, request, redirect, url_for
from werkzeug.wrappers import Response

from src.models import Budget, Transaction
from src.utils import (
    get_categories_by_type,
    get_budget_by_category,
    calculate_expense,
    get_budgets
)
from src import config
from .. import db

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget')
def budget() -> str:
    """
    Renders the budget overview page.

    :return: The rendered budget template.
    """
    categories = get_categories_by_type('expense')
    budgets = get_budgets()
    return render_template('budget.html', categories=categories,
                           budgets=budgets, default_currency=config.DEFAULT_CURRENCY)

@budget_bp.route('/budget-set', methods=['POST'])
def budget_set() -> Response:
    """
    Handles setting or updating a budget for a specific category.

    :return: Redirects to the budget page after processing the request.
    """
    if request.method == 'POST':
        category_id = request.form.get('category_select')
        total_budget = request.form['total_budget'].strip()

        new_budget = None
        if category_id is None:
            category_id = 0

        budget_category = get_budget_by_category(int(category_id))
        if budget_category is None:
            if category_id != 0:
                sum_amount = sum(el[0].amount for el in db.session.execute(
                    db.select(Transaction).filter_by(category_id=category_id)))
            else:
                sum_amount = calculate_expense()
            new_budget = Budget(category_id=int(category_id),
                                current_budget=sum_amount,
                                total_budget=float(total_budget))
        else:
            budget_category.total_budget = float(total_budget)

        if new_budget is not None:
            db.session.add(new_budget)

        db.session.commit()

        return redirect(url_for('budget.budget'))

    return redirect(url_for('budget.budget'))

@budget_bp.route('/budget-remove', methods=['POST'])
def budget_remove() -> Response:
    """
    Handles the removal of a budget based on the provided budget ID.

    :return: Redirects to the budget page after processing the request.
    """
    if request.method == 'POST':
        budget_id = request.form['budget_id']
        budget_to_remove = db.session.execute(db.select(Budget).
                                    filter_by(id=budget_id)).scalar_one_or_none()
        db.session.delete(budget_to_remove)
        db.session.commit()

        return redirect(url_for('budget.budget'))

    return redirect(url_for('budget.budget'))
