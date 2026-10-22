from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ---------------------------------------------------------
# CURRENT MONTH CATEGORY BREAKDOWN & TOTAL SUMMARY
# ---------------------------------------------------------
@router.get("/summary", response_model=schemas.MonthSummaryResponse)
def get_spending_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    total_spent = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == current_user.id
    ).scalar() or 0.0

    category_data = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total_amount")
    ).filter(
        models.Expense.user_id == current_user.id
    ).group_by(
        models.Expense.category
    ).all()

    breakdown = [
        schemas.CategorySpend(category=row[0] or "Uncategorized", total_amount=float(row[1]))
        for row in category_data
    ]

    return {
        "total_spending": total_spent,
        "category_breakdown": breakdown
    }


# ---------------------------------------------------------
# MONTHLY SPENDING TREND (Line Chart Data)
# ---------------------------------------------------------
@router.get("/trend", response_model=List[schemas.MonthlyTrendItem])
def get_spending_trend(
    months: int = Query(default=6, ge=1, le=24, description="Number of past months to retrieve"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Calculate cutoff date based on requested months
    cutoff_date = datetime.utcnow() - timedelta(days=months * 30)

    # Format date as 'YYYY-MM' directly in PostgreSQL for grouping
    month_label = func.to_char(models.Expense.date, "YYYY-MM").label("month_str")

    trend_query = db.query(
        month_label,
        func.sum(models.Expense.amount).label("total_spent")
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= cutoff_date
    ).group_by(
        month_label
    ).order_by(
        month_label.asc()
    ).all()

    return [
        schemas.MonthlyTrendItem(
            month=row[0],
            total_amount=float(row[1])
        )
        for row in trend_query
    ]