from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)

    # Relationships
    expenses = relationship("Expense", back_populates="owner")
    categories = relationship("Category", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, default="expense")  # expense ya income
    color = Column(String, default="#3B82F6")  # UI color code
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category_rel")
    budgets = relationship("Budget", back_populates="category")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)  # Purane data ke compatibility ke liye
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="expenses")
    category_rel = relationship("Category", back_populates="expenses")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    monthly_limit = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # Example: "2026-10"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")