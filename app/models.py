from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime 
from . import db

class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    category_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'income' or 'expense'

    # Връзка към Transaction
    transactions: Mapped[list['Transaction']] = relationship(back_populates='category', lazy=True)


class Transaction(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=False)

    # Връзка към Category
    category: Mapped['Category'] = relationship(back_populates='transactions')

