from flask import render_template, Blueprint, request, redirect, url_for
import config
from requests.exceptions import HTTPError
from .. import db
from utils import get_transactions, get_currency_codes, get_exchange_rate, save_default_currency

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
def settings():
    available_currencies = get_currency_codes()
    return render_template('settings.html', available_currencies=available_currencies, default_currency=config.default_currency)

@settings_bp.route('/settings-save', methods=['POST'])
def settings_save():
    if request.method == 'POST':
        from_currency = config.default_currency
        config.default_currency = request.form['default_currency']

        save_default_currency(config.default_currency)

        try:
            exchange_rate = get_exchange_rate(from_currency, config.default_currency)
        except HTTPError as http_err:
            #flash
            print(f'HTTP error occurred: {http_err}')

        transactions = get_transactions()
        for transaction in transactions:
            transaction.amount *= exchange_rate
        db.session.commit()

        return redirect(url_for('settings.settings'))

    return redirect(url_for('settings.settings'))



