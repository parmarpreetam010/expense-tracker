from datetime import datetime
from typing import List, Optional, Literal

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, asc, desc
from sqlalchemy.orm import Session

from app import models, schemas, security, auth
from app.database import get_db

app = FastAPI(title="Expense Tracker")


# ---------------------------------------------------------
# AUTH ROUTE 1: User Sign-Up / Registration (POST)
# ---------------------------------------------------------
@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    encrypted_password = security.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=encrypted_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------------------------------------------------------
# AUTH ROUTE 2: User Login & Token Generation (POST)
# ---------------------------------------------------------
@app.post("/login", response_model=schemas.Token)
def login_user(
    user_credentials: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    if not user or not security.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password"
        )
        
    access_token = auth.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------
# EXPENSE ROUTE 1: Create a new expense (POST) - LOCKED 🔒
# ---------------------------------------------------------
@app.post("/expenses", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        user_id=current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


# ---------------------------------------------------------
# EXPENSE ROUTE 2: Get MY expenses (GET) - LOCKED 🔒
# Added: Pagination, Filters, and Sorting
# ---------------------------------------------------------
@app.get("/expenses", response_model=schemas.PaginatedExpenseResponse)
def get_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
    # Pagination
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    # Filters
    category: Optional[str] = Query(default=None, description="Filter by category"),
    start_date: Optional[datetime] = Query(default=None, description="Start date (YYYY-MM-DD or full ISO)"),
    end_date: Optional[datetime] = Query(default=None, description="End date (YYYY-MM-DD or full ISO)"),
    # Sorting
    sort_by: Literal["date", "amount"] = Query(default="date", description="Sort by date or amount"),
    order: Literal["asc", "desc"] = Query(default="desc", description="Sort direction")
):
    # 1. Base query strictly scoped to logged-in user
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    # 2. Dynamic Filtering
    if category:
        query = query.filter(models.Expense.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    # 3. Calculate total count for matching records
    total_records = query.count()

    # 4. Dynamic Sorting
    sort_column = models.Expense.amount if sort_by == "amount" else models.Expense.date
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(sort_column))

    # 5. Apply Pagination
    expenses = query.offset(offset).limit(limit).all()

    return {
        "total_records": total_records,
        "limit": limit,
        "offset": offset,
        "data": expenses
    }


# ---------------------------------------------------------
# EXPENSE ROUTE 3: Delete my expense by ID (DELETE) - LOCKED 🔒
# ---------------------------------------------------------
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id, 
        models.Expense.user_id == current_user.id
    ).first()
    
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    db.delete(db_expense)
    db.commit()
    return None


# ---------------------------------------------------------
# EXPENSE ROUTE 4: Update my expense by ID (PUT) - LOCKED 🔒
# ---------------------------------------------------------
@app.put("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int, 
    updated_expense: schemas.ExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id, 
        models.Expense.user_id == current_user.id
    ).first()
    
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    db_expense.title = updated_expense.title
    db_expense.amount = updated_expense.amount
    db_expense.category = updated_expense.category
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


# ---------------------------------------------------------
# ANALYTICS ROUTE: Get Totals and Category Breakdown (GET) - LOCKED 🔒
# ---------------------------------------------------------
@app.get("/analytics/summary", response_model=schemas.MonthSummaryResponse)
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


# ---------------------------------------------------------
# ROUTE 5: Health Check (GET)
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}