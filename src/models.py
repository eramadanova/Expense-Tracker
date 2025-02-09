"""
    Defines database models for the application.
"""

from typing import List, Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import db

class Category(db.Model):
    """
    Represents a category in the application.

    Attributes:
        id (int): The unique identifier for the category.
        name (str): The name of the category (unique and not nullable).
        category_type (str): The type of the category ('income' or 'expense').
        transactions (list[Transaction]): A list of transactions associated with this category.
        budget (Budget): The budget associated with this category.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    category_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'income' or 'expense'

    transactions: Mapped[List['Transaction']] = relationship(back_populates='category', lazy=True)
    budget: Mapped[Optional['Budget']] = relationship(back_populates='category')

    def __repr__(self) -> str:
        """
        Returns a string representation of the Category instance.

        :return: A string describing the Category.
        """
        return f'Category(name={self.name}, category_type={self.category_type})'

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the Category instance.

        :return: A formatted string with category details.
        """
        return f'<Category {self.name}, Type: {self.category_type}>'


class Transaction(db.Model):
    """
    Represents a transaction in the application.

    Attributes:
        id (int): The unique identifier for the transaction.
        category_id (int): The ID of the category associated with this transaction.
        description (str): A description of the transaction.
        amount (float): The amount of the transaction (not nullable).
        date (str): The date of the transaction (not nullable).
        category (Category): The category associated with this transaction.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)

    category: Mapped['Category'] = relationship(back_populates='transactions')

    def __repr__(self) -> str:
        """
        Returns a string representation of the Transaction instance.

        :return: A string describing the Transaction.
        """
        return f"""Transaction(
        category_id={self.id},
        description={self.description},
        amount={self.amount},
        date={self.date}
        )"""

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the Transaction instance.

        :return: A formatted string with transaction details.
        """
        return f'<Transaction {self.description}, Amount: {self.amount}, Date: {self.date}>'

class Budget(db.Model):
    """
    Represents a budget in the application.

    Attributes:
        id (int): The unique identifier for the budget.
        category_id (int): The ID of the category associated with this budget.
        current_budget (float): The current budget amount (not nullable).
        total_budget (float): The total budget amount (not nullable).
        category (Category): The category associated with this budget.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    current_budget: Mapped[float] = mapped_column(nullable=False)
    total_budget: Mapped[float] = mapped_column(nullable=False)

    category: Mapped['Category'] = relationship(back_populates='budget')

    def __repr__(self) -> str:
        """
        Returns a string representation of the Budget instance.

        :return: A string describing the Budget.
        """
        return f"""Budget(
        current_expense={self.current_budget},
        max_expense={self.total_budget},
        )"""

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the Budget instance.

        :return: A formatted string with budget details.
        """
        return f'<Current_expense {self.current_budget}, Max_expense: {self.total_budget}>'
