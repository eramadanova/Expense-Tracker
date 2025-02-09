"""
Validation utilities for transaction data processing.
"""

from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from flask import flash
from werkzeug.datastructures import FileStorage

from src.models import Transaction
from src import config
from src.utils import get_category_by_name
from src.utils_api import get_currency_codes, get_exchange_rate

def is_valid(transaction_category: Optional[str], transaction_amount: str) -> bool:
    """
    Validates if transaction category and amount are provided.

    :param transaction_category: The category of the transaction.
    :param transaction_amount: The amount of the transaction.
    :return: True if valid, False otherwise.
    """
    if transaction_category is None:
        flash('Category cannot be empty!', 'danger')
        return False
    if transaction_amount == '':
        flash('Amount cannot be empty!', 'danger')
        return False
    return True

def validate_file(file: FileStorage) -> bool:
    """
    Validates the uploaded file.

    :param file: The uploaded file.
    :return: True if the file is a valid CSV, False otherwise.
    """
    if not file or file.filename == '':
        flash('No file selected!', 'danger')
        return False
    if not file.filename.endswith('.csv'):
        flash('Invalid file format! Please upload a CSV file.', 'danger')
        return False
    return True

def validate_columns(df: pd.DataFrame) -> bool:
    """
    Validates if the CSV file contains the required columns.

    :param df: The dataframe loaded from the CSV file.
    :return: True if valid, False otherwise.
    """
    if df.empty:
        flash('CSV file is empty!', 'danger')
        return False
    required_columns = {'date', 'category', 'description', 'amount', 'currency'}
    if not required_columns.issubset(df.columns):
        flash(f'Invalid CSV format! Expected columns: {", ".join(required_columns)}', 'danger')
        return False
    return True

def extract_and_validate_category(row: Dict[str, Optional[str]], index: int) -> str:
    """
    Extracts and validates the category field from a row.

    :param row: The row of data.
    :param index: The index of the row.
    :return: The validated category name.
    :raises ValueError: If the category is missing or invalid.
    """
    category_name = row.get('category')
    if pd.isna(category_name) or category_name is None or category_name.strip() == '':
        raise ValueError(f'Invalid or missing category on row {index+1}')
    return category_name.strip()

def extract_and_validate_description(row: Dict[str, Optional[str]]) -> str:
    """
    Extracts and validates the description field from a row.

    :param row: The row of data.
    :return: The validated description.
    """
    description = row.get('description')
    return '' if pd.isna(description) or description is None else str(description).strip()

def extract_and_validate_amount(row: Dict[str, Optional[str]], index: int) -> float:
    """
    Extracts and validates the amount field from a row.

    :param row: The row of data.
    :param index: The index of the row.
    :return: The validated amount as a float.
    :raises ValueError: If the amount is missing, not a number, or non-positive.
    """
    amount_str = row.get('amount')
    if pd.isna(amount_str) or amount_str is None or amount_str == '':
        raise ValueError(f'Invalid amount on row {index+1}')
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError(f'Invalid amount \'{amount}\' on row {index+1}')
    except ValueError as exc:
        raise ValueError(f'Amount \'{amount_str}\' is not a valid number on row {index+1}') from exc

    return amount

def extract_and_validate_date(row: Dict[str, Optional[str]], index: int) -> datetime:
    """
    Extracts and validates the date field from a row.

    :param row: The row of data.
    :param index: The index of the row.
    :return: The validated date as a datetime object.
    :raises ValueError: If the date format is incorrect.
    """
    date_str = row.get('date')
    if pd.isna(date_str) or date_str is None or date_str.strip() == '':
        raise ValueError(f'Invalid or missing date on row {index+1}')
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as exc:
        raise ValueError(f"""Invalid date \'{date_str}\'!
                          Expected format: YYYY-MM-DD on row {index+1}""") from exc

def extract_and_validate_currency(row: Dict[str, Optional[str]], index: int) -> str:
    """
    Extracts and validates the currency field from a row.

    :param row: The row of data.
    :param index: The index of the row.
    :return: The validated currency code.
    :raises ValueError: If the currency is missing.
    """
    currency = row.get('currency')
    if pd.isna(currency) or currency is None or currency.strip() == '':
        raise ValueError(f'Invalid or missing currency on row {index+1}')
    return currency.strip()

def process_transaction(row: Dict[str, Optional[str]], index: int) -> Optional[Transaction]:
    """
    Processes a transaction from a row of data.

    :param row: The row of data.
    :param index: The index of the row.
    :return: A Transaction object if valid, None otherwise.
    """
    try:
        category_name = extract_and_validate_category(row, index)
        description = extract_and_validate_description(row)
        amount = extract_and_validate_amount(row, index)
        date_obj = extract_and_validate_date(row, index)
        currency = extract_and_validate_currency(row, index)

        category = get_category_by_name(category_name)
        if not category:
            raise ValueError(f'Non-existing category "{category_name}" on row {index+1}')

        amount = validate_currency(currency, amount)

        return Transaction(
            category_id=category.id,
            description=description,
            amount=amount,
            date=date_obj.strftime('%Y-%m-%d')
        )
    except ValueError as e:
        flash(str(e), 'danger')
        return None

def validate_currency(currency: str, amount: float) -> float:
    """
    Validates and converts an amount to the default currency if needed.

    :param currency: The currency code of the transaction.
    :param amount: The transaction amount.
    :return: The converted amount in the default currency.
    """
    currency_codes = get_currency_codes()
    if currency not in currency_codes:
        currency = 'BGN'
    elif currency != config.DEFAULT_CURRENCY:
        exchange_rate = get_exchange_rate(currency, config.DEFAULT_CURRENCY)
        amount *= exchange_rate
    return amount
