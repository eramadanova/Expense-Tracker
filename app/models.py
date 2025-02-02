from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db

class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    category_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'income' or 'expense'

    # Връзка към Transaction
    transactions: Mapped[list['Transaction']] = relationship(back_populates='category', lazy=True)

    def __repr__(self):
        return f"Category(name={self.name}, category_type={self.category_type})"

    def __str__(self):
        return f"<Category {self.name}, Type: {self.category_type}>"


class Transaction(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)

    # Връзка към Category
    category: Mapped['Category'] = relationship(back_populates='transactions')

    def __repr__(self):
        return f"""Transaction(
        category_id={self.id},
        description={self.description},
        amount={self.amount},
        date={self.date}
        )"""

    def __str__(self):
        return f"<Transaction {self.description}, Amount: {self.amount}, Date: {self.date}>"
