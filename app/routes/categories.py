from flask import render_template, Blueprint, request, flash, redirect, url_for
from ..models import Category, Transaction, Budget
from .. import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def categories():
    expense_categories = [
        el[0] for el in db.session.execute(
            db.select(Category).filter_by(category_type='expense')
        )]
    income_categories = [
        el[0] for el in db.session.execute(
            db.select(Category).filter_by(category_type='income')
        )]
    return render_template('categories.html',
                           expense_categories=expense_categories,
                           income_categories=income_categories)

@categories_bp.route('/categories-add', methods=['POST'])
def categories_add():
    if request.method == 'POST':
        category_type = request.form['category_type']
        name = request.form['category_name'].strip()

        if not name:
            #flash("Category name cannot be empty.", "error")
            return redirect(url_for('categories.categories'))

        if category_type not in ('income', 'expense'):
            #flash("Invalid category type.", "error")
            return redirect(url_for('categories.categories'))

        existing_category = db.session.execute(
            db.select(Category).filter_by(name=name, category_type=category_type)
            ).scalar_one_or_none()
        if existing_category:
            #flash("Category already exists.", "error")
            return redirect(url_for('categories.categories'))

        new_category = Category(name=name, category_type=category_type)
        db.session.add(new_category)
        db.session.commit()
        #flash("Category added successfully!", "success")
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories-update', methods=['POST'])
def categories_update():
    if request.method == 'POST':
        category_id = request.form['category_id']
        updated_name = request.form['update_category_name'].strip()

        # Check if category with this name exists
        existing_category = db.session.execute(
            db.select(Category).filter_by(name=updated_name)
            ).scalar_one_or_none()

        if existing_category is not None:
            flash("Category with this name already exists.", "error")
            return redirect(url_for('categories.categories'))

        # Find category by ID
        category = db.session.execute(
                   db.select(Category).filter_by(id=category_id)
                   ).scalar_one_or_none()

        if category is None:
            flash("Category not found.", "error")
            return redirect(url_for('categories.categories'))

        # Update name
        category.name = updated_name
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories-delete', methods=['POST'])
def categories_delete():
    if request.method == 'POST':
        category_id = request.form['category_id']
        # print(category_id)

        # Find category by ID
        category = db.session.execute(
            db.select(Category).filter_by(id=category_id)
            ).scalar_one_or_none()

        if category is None:
            #flash("Category not found.", "error")
            return redirect(url_for('categories.categories'))

        # Delete category
        db.session.query(Transaction).filter_by(category_id=category_id).delete()
        db.session.query(Budget).filter_by(category_id=category_id).delete()
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully!", "success")
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))
