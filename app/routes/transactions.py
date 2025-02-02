from flask import render_template, Blueprint

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
def transactions():
    return render_template('transactions.html')
