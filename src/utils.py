"""
Utility functions for database operations and currency handling.
"""

from typing import List, Optional

from src import db
from src.models import Transaction, Category, Budget

def get_transactions() -> List[Transaction]:
    """
    Fetch all transactions from the database.

    :return: A list of all transactions.
    """
    return [el[0] for el in db.session.execute(db.select(Transaction))]

def get_categories() -> List[Category]:
    """
    Fetch all categories from the database.

    :return: A list of all categories.
    """
    return [el[0] for el in db.session.execute(db.select(Category))]

def get_budgets() -> List[Budget]:
    """
    Fetch all budgets from the database.

    :return: A list of all budgets.
    """
    return [el[0] for el in db.session.execute(db.select(Budget))]

def get_categories_by_type(category_type: str) -> List[Category]:
    """
    Fetch categories filtered by type.

    :param category_type: The type of category (e.g., 'expense', 'income').
    :return: A list of categories of the given type.
    """
    return [el[0] for el in db.session.execute(db.select(Category)
                                               .filter_by(category_type=category_type))]

def get_category_by_name(category_name: str) -> Optional[Category]:
    """
    Fetch a category by its name.

    :param category_name: The name of the category.
    :return: The category object if found, else None.
    """
    return db.session.execute(
        db.select(Category).filter_by(name=category_name)
        ).scalar_one_or_none()

def get_category_by_id(category_id: int) -> Optional[Category]:
    """
    Fetch a category by its ID.

    :param category_id: The ID of the category.
    :return: The category object if found, else None.
    """
    return db.session.execute(
            db.select(Category).filter_by(id=category_id)
            ).scalar_one_or_none()

def get_transaction_by_id(transaction_id: int) -> Optional[Transaction]:
    """
    Fetch a transaction by its ID.

    :param transaction_id: The ID of the transaction.
    :return: The transaction object if found, else None.
    """
    return db.session.execute(
            db.select(Transaction).filter_by(id=transaction_id)
            ).scalar_one_or_none()


def get_transactions_by_type(transactions: List[Transaction],
                            category_type:str) -> List[Transaction]:
    """
    Filters transactions based on the category type (e.g., 'expense' or 'income').

    :param transactions: List of transactions.
    :param category_type: The category type to filter by.

    :return: Filtered list of transactions.
    """
    return [transaction for transaction in transactions
            if transaction.category.category_type == category_type]

def calculate_income() -> float:
    """
    Calculate the total income from transactions.

    :return: The total income amount.
    """
    transactions = [el[0].amount for el in
                    db.session.execute(db.select(Transaction)
                                       .filter(Transaction.category.has(category_type='income')))]
    return sum(transactions)

def calculate_expense() -> float:
    """
    Calculate the total expense from transactions.

    :return: The total expense amount.
    """
    transactions = [el[0].amount for el in
                    db.session.execute(db.select(Transaction)
                                       .filter(Transaction.category.has(category_type='expense')))]
    return sum(transactions)

def get_budget_by_category(category_id: int) -> Optional[Budget]:
    """
    Fetch the budget for a given category.

    :param category_id: The ID of the category.
    :return: The budget object if found, else None.
    """
    return db.session.execute(
        db.select(Budget).filter_by(category_id=category_id)
    ).scalar_one_or_none()

def add_budget_expense(budget: Optional[Budget], transaction_amount: float) -> None:
    """
    Add an expense to the budget.

    :param budget: The budget object.
    :param transaction_amount: The amount to add to the budget.
    """
    try:
        transaction_amount = float(transaction_amount)
    except ValueError as exc:
        raise ValueError('Invalid transaction amount. Must be a number.') from exc

    if budget is not None:
        budget.current_budget += transaction_amount
        db.session.commit()

def update_budget_expense(budget: Optional[Budget],
                          current_amount: float,
                          updated_amount: float) -> None:
    """
    Update an expense in the budget.

    :param budget: The budget object.
    :param current_amount: The current expense amount.
    :param updated_amount: The new expense amount.
    """
    try:
        updated_amount = float(updated_amount)
    except ValueError as exc:
        raise ValueError('Invalid transaction amount. Must be a number.') from exc

    if budget is not None:
        budget.current_budget += (updated_amount - current_amount)
        db.session.commit()

def delete_budget_expense(transaction: Transaction, budget: Optional[Budget]) -> None:
    """
    Delete an expense from the budget.

    :param transaction: The transaction object.
    :param budget: The budget object.
    """
    if budget is not None:
        budget.current_budget -= transaction.amount
        db.session.commit()

def create_transaction(category_id: int, description: str, amount: float, date: str) -> Transaction:
    """
    Creates and saves a new transaction in the database.

    :param category_id: The ID of the category associated with the transaction.
    :param description: A brief description of the transaction.
    :param amount: The amount of the transaction (expected as a numeric value).
    :param date: The date of the transaction in 'YYYY-MM-DD' format.
    :return: The newly created Transaction object.
    :raises ValueError: If the amount is not a valid number.
    """
    try:
        amount = float(amount)
    except ValueError as exc:
        raise ValueError('Invalid transaction amount.') from exc

    new_transaction = Transaction(
        category_id=category_id,
        description=description.strip(),
        amount=amount,
        date=date
    )

    db.session.add(new_transaction)
    db.session.commit()

    return new_transaction


def update_currency(exchange_rate: float) -> None:
    """
    Update transaction and budget amounts based on the exchange rate.

    :param exchange_rate: The exchange rate to apply.
    """
    transactions = get_transactions()
    for transaction in transactions:
        transaction.amount *= exchange_rate

    budgets = get_budgets()
    for budget in budgets:
        budget.current_budget *= exchange_rate
        budget.total_budget *= exchange_rate
