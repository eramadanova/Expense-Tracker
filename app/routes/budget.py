from flask import render_template, Blueprint, request, redirect, url_for
from utils import get_categories_by_type, get_budget_by_category, get_transactions, get_budgets
from .. import db
from app.models import Budget, Transaction
import config

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget')
def budget():
    categories = get_categories_by_type("expense")
    budgets = get_budgets()
    return render_template('budget.html', categories=categories, budgets=budgets, default_currency=config.default_currency)

@budget_bp.route('/budget-set', methods=['POST'])
def budget_set():
    if request.method == 'POST':
        category_id = request.form.get('category_select')
        total_budget = request.form.get('total_budget')

        new_budget = None
        if category_id is None:
            category_id = 0

        budget = get_budget_by_category(category_id)
        if budget is None:
            if category_id != 0:
                sumAmount = sum([el[0].amount for el in db.session.execute(db.select(Transaction).filter_by(category_id=category_id))])
            else:
                sumAmount = sum([el.amount  for el in get_transactions()])
            new_budget = Budget(category_id=category_id, current_budget=sumAmount, total_budget=total_budget)
        else:
            budget.total_budget = total_budget

        if new_budget is not None:
            db.session.add(new_budget)

        db.session.commit()

        return redirect(url_for('budget.budget'))

    return redirect(url_for('budget.budget'))

