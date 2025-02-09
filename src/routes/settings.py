"""
    Defines settings-related routes for managing currency preferences.
"""

from typing import Union
from flask import render_template, Blueprint, request, redirect, url_for, flash
from requests.exceptions import HTTPError
from werkzeug.wrappers import Response

from src import config
from src.utils import update_currency
from src.utils_api import (
    get_currency_codes,
    get_exchange_rate,
    save_default_currency
)
from .. import db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def settings() -> str:
    """
    Renders the settings page with available currency options.

    :return: Rendered settings template with currency data.
    """
    available_currencies = get_currency_codes()
    return render_template(
        'settings.html',
        available_currencies=available_currencies,
        default_currency=config.DEFAULT_CURRENCY
    )

@settings_bp.route('/settings-save', methods=['POST'])
def settings_save() -> Union[str, Response]:
    """
    Updates the default currency setting and fetches the exchange rate.

    If an API error occurs while fetching exchange rates, a flash message is displayed.
    The new currency is saved in the configuration and database.

    :return: Redirect to the settings page.
    """
    if request.method == 'POST':
        from_currency = config.DEFAULT_CURRENCY
        config.DEFAULT_CURRENCY = request.form['default_currency'].strip()

        save_default_currency(config.DEFAULT_CURRENCY)

        try:
            exchange_rate = get_exchange_rate(from_currency, config.DEFAULT_CURRENCY)
        except HTTPError:
            flash('API not working', 'danger')
            return redirect(url_for('settings.settings'))

        update_currency(exchange_rate)
        db.session.commit()
        flash('Currency successfully updated.', 'success')
        return redirect(url_for('settings.settings'))

    return redirect(url_for('settings.settings'))
