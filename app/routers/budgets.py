from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from pydantic import BaseModel
from typing import Optional

from app import models
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])

class BudgetSetRequest(BaseModel):
    monthly_limit: float
    month: Optional[int] = None
    year: Optional[int] = None

@router.post("", status_code=status.HTTP_200_OK)
def set_monthly_budget(
    payload: BudgetSetRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    target_month = payload.month or today.month
    target_year = payload.year or today.year

    budget = (
        db.query(models.Budget)
        .filter(
            models.Budget.user_id == current_user.id,
            models.Budget.month == target_month,
            models.Budget.year == target_year,
        )
        .first()
    )

    if budget:
        budget.monthly_limit = payload.monthly_limit
    else:
        budget = models.Budget(
            user_id=current_user.id,
            monthly_limit=payload.monthly_limit,
            month=target_month,
            year=target_year,
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)
    return {"message": "Budget limit updated successfully", "monthly_limit": budget.monthly_limit}

@router.get("/status")
def get_budget_status(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    budget = (
        db.query(models.Budget)
        .filter(
            models.Budget.user_id == current_user.id,
            models.Budget.month == target_month,
            models.Budget.year == target_year,
        )
        .first()
    )
    monthly_limit = float(budget.monthly_limit) if budget else 0.0

    actual_spending = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0.0))
        .filter(
            models.Expense.user_id == current_user.id,
            func.extract("month", models.Expense.date) == target_month,
            func.extract("year", models.Expense.date) == target_year,
        )
        .scalar()
    )
    actual_spending = float(actual_spending)

    percentage_used = round((actual_spending / monthly_limit * 100), 1) if monthly_limit > 0 else 0.0

    status_flag = "SAFE"
    if monthly_limit > 0:
        if percentage_used >= 100:
            status_flag = "OVERSPENT"
        elif percentage_used >= 80:
            status_flag = "WARNING"

    return {
        "monthly_limit": monthly_limit,
        "actual_spending": actual_spending,
        "percentage_used": percentage_used,
        "status": status_flag,
        "month": target_month,
        "year": target_year,
    }