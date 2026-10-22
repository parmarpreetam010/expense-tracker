from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

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
        schemas.CategorySpend(category=row[0], total_amount=float(row[1])) 
        for row in category_data
    ]
    
    return {
        "total_spending": total_spent,
        "category_breakdown": breakdown
    }