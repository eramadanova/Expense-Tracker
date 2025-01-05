from flask import render_template, Blueprint, request, flash, redirect, url_for
from ..models import Category, Transaction
from .. import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def categories():
    expense_categories = [el[0] for el in db.session.execute(db.select(Category).filter_by(category_type='expense'))]
    income_categories = [el[0] for el in db.session.execute(db.select(Category).filter_by(category_type='income'))]
    return render_template('categories.html', expense_categories=expense_categories, income_categories=income_categories)

@categories_bp.route('/categories_add', methods=['POST'])
def categories_add():
    category_type = request.form['categoryType']
    name = request.form['categoryName'].strip()

    if not name:
        flash("Category name cannot be empty.", "error")
        return redirect(url_for('categories.categories'))

    if category_type not in ('income', 'expense'):
        flash("Invalid category type.", "error")
        return redirect(url_for('categories.categories'))

    existing_category = db.session.execute(db.select(Category).filter_by(name=name, category_type=category_type)).first()
    if existing_category:
        flash("Category already exists.", "error")
        return redirect(url_for('categories.categories'))

    new_category = Category(name=name, category_type=category_type)
    db.session.add(new_category)
    db.session.commit()
    flash("Category added successfully!", "success")
    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories_update', methods=['POST'])
def categories_update():
    if request.method == 'POST':
        category_id = request.form['category_id']
        updated_name = request.form['updateCategoryName'].strip()

        # Проверка дали съществува категория със същото име
        existing_category = db.session.execute(
                            db.select(Category).filter_by(name=updated_name)
                            ).scalar_one_or_none()

        if existing_category is not None:
            flash("Category with this name already exists.", "error")
            return redirect(url_for('categories.categories'))

        # Намерете категорията по ID
        category = db.session.execute(
                   db.select(Category).filter_by(id=category_id)
                   ).scalar_one_or_none()

        if category is None:
            flash("Category not found.", "error")
            return redirect(url_for('categories.categories'))

        # Актуализирайте името
        category.name = updated_name
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories_delete', methods=['POST'])
def categories_delete():
    if request.method == 'POST':
        category_id = request.form['category_id']

        # Намерете категорията по ID
        category = db.session.execute(
                db.select(Category).filter_by(id=category_id)
                ).scalar_one_or_none()

        if category is None:
            flash("Category not found.", "error")
            return redirect(url_for('categories.categories'))

        # Изтрийте категорията
        db.session.delete(category)
        db.session.query(Transaction).filter_by(category_id=category.id).delete()
        db.session.commit()
        flash("Category deleted successfully!", "success")
        return redirect(url_for('categories.categories'))

    return redirect(url_for('categories.categories'))
