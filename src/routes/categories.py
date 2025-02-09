"""
    Defines category-related routes for the Flask application.
"""

from flask import render_template, Blueprint, request, flash, redirect, url_for, Response
from typing import List, Optional, Union
from werkzeug.wrappers import Response as WerkzeugResponse

from src.utils import (
    get_categories_by_type,
    get_category_by_name,
    get_category_by_id
)
from src.models import Category, Transaction, Budget
from .. import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def categories() -> str:
    """
    Renders the categories page with a list of income and expense categories.

    :return: The rendered categories template.
    """
    expense_categories = get_categories_by_type('expense')
    income_categories = get_categories_by_type('income')
    return render_template('categories.html',
                           expense_categories=expense_categories,
                           income_categories=income_categories)

@categories_bp.route('/categories-add', methods=['POST'])
def categories_add() -> Union[Response, WerkzeugResponse]:
    """
    Handles adding a new category based on user input.

    :return: Redirects to the categories page after processing the request.
    """
    if request.method == 'POST':
        category_type = request.form['category_type']
        name = request.form['category_name']

        if category_type not in ('income', 'expense'):
            flash('Invalid category type.', 'danger')
            return redirect(url_for('categories.categories'))

        if name.strip() == '':
            flash('Category name cannot be empty.', 'danger')
            return redirect(url_for('categories.categories'))

        name = name.strip()

        existing_category = db.session.execute(
            db.select(Category).filter_by(name=name, category_type=category_type)
            ).scalar_one_or_none()
        if existing_category:
            flash('Category already exists.', 'danger')
            return redirect(url_for('categories.categories'))

        new_category = Category(name=name, category_type=category_type)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories-update', methods=['POST'])
def categories_update() -> Union[Response, WerkzeugResponse]:
    """
    Handles updating an existing category's name.

    :return: Redirects to the categories page after processing the update.
    """
    if request.method == 'POST':
        category_id = request.form['category_id']
        updated_name = request.form['update_category_name'].strip()

        existing_category = get_category_by_name(updated_name)
        if existing_category is not None:
            flash('Category with this name already exists.', 'danger')
            return redirect(url_for('categories.categories'))

        category = get_category_by_id(category_id)
        if category is None:
            flash('Category not found.', 'danger')
            return redirect(url_for('categories.categories'))

        category.name = updated_name
        db.session.commit()
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories-delete', methods=['POST'])
def categories_delete() -> Union[Response, WerkzeugResponse]:
    """
    Handles deleting a category along with its related transactions and budgets.

    :return: Redirects to the categories page after deletion.
    """
    if request.method == 'POST':
        category_id = request.form['category_id']

        category = get_category_by_id(category_id)
        if category is None:
            flash('Category not found.', 'danger')
            return redirect(url_for('categories.categories'))

        db.session.query(Transaction).filter_by(category_id=category_id).delete()
        db.session.query(Budget).filter_by(category_id=category_id).delete()
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))
