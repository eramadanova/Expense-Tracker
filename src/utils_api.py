"""
Utility functions for interacting with currency-related API.
This module provides functions to fetch currency codes, exchange rates
and manage default currency settings.
"""

import os
from typing import List

import requests

from src.config import BASE_URL

def get_currency_codes() -> List[str]:
    """
    Retrieve supported currency codes from the external API.

    :return: A list of supported currency codes.
    """
    url = f"{BASE_URL}/codes"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [code[0] for code in data['supported_codes']]
    except requests.RequestException:
        return ['USD', 'EUR', 'BGN']  # Default fallback

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Fetch the exchange rate between two currencies.

    :param from_currency: The base currency.
    :param to_currency: The target currency.
    :return: The exchange rate.
    """
    url = f"{BASE_URL}/pair/{from_currency}/{to_currency}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('conversion_rate', 1)
    except requests.RequestException:
        return 1

def load_default_currency() -> str:
    """
    Load the default currency from a file.

    :return: The default currency code.
    """
    if os.path.exists('currency.txt'):
        with open(os.path.join('currency.txt'), 'r', encoding='utf-8') as fp:
            default_currency = fp.read()

        currency_codes = get_currency_codes()
        default_currency = default_currency if default_currency in currency_codes else 'BGN'
    else:
        default_currency = 'BGN'

    return default_currency

def save_default_currency(currency: str) -> None:
    """
    Save the default currency to a file.

    :param currency: The currency code to save.
    """
    with open(os.path.join('currency.txt'), 'w', encoding='utf-8') as fp:
        fp.write(currency)
