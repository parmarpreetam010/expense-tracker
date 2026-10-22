from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/budgets", tags=["Budgets"])

# ---------------------------------------------------------
# SET OR UPDATE A BUDGET (POST /budgets)
# ---------------------------------------------------------
@router.post("", response_model=schemas.BudgetResponse, status_code=status.HTTP_201_CREATED)
def set_budget(
    budget: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Verify category belongs to the logged-in user
    category = db.query(models.Category).filter(
        models.Category.id == budget.category_id,
        models.Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # 2. Update existing budget if one is already set for this month
    existing_budget = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.category_id == budget.category_id,
        models.Budget.month == budget.month
    ).first()

    if existing_budget:
        existing_budget.monthly_limit = budget.monthly_limit
        db.commit()
        db.refresh(existing_budget)
        return existing_budget

    # 3. Create a new budget record
    new_budget = models.Budget(
        user_id=current_user.id,
        category_id=budget.category_id,
        monthly_limit=budget.monthly_limit,
        month=budget.month
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


# ---------------------------------------------------------
# GET ALL BUDGETS WITH USAGE % (GET /budgets?month=YYYY-MM)
# ---------------------------------------------------------
@router.get("", response_model=List[schemas.BudgetResponse])
def get_budgets(
    month: str,  # Format: "YYYY-MM" (e.g., "2026-10")
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.month == month
    ).all()

    result = []
    for b in budgets:
        # Sum total expenses under this category for the user
        total_spent = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == current_user.id,
            models.Expense.category_id == b.category_id
        ).scalar() or 0.0

        percentage = (total_spent / b.monthly_limit * 100.0) if b.monthly_limit > 0 else 0.0

        result.append(
            schemas.BudgetResponse(
                id=b.id,
                category_id=b.category_id,
                monthly_limit=b.monthly_limit,
                month=b.month,
                user_id=b.user_id,
                total_spent=round(total_spent, 2),
                percentage_used=round(percentage, 1)
            )
        )
    return result