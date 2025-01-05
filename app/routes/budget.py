from flask import render_template, Blueprint

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget')
def budget():
    return render_template('budget.html')
