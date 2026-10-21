from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import engine, get_db

app = FastAPI(title="Expense Tracker")

# ---------------------------------------------------------
# ROUTE 1: Create a new expense (POST)
# ---------------------------------------------------------
@app.post("/expenses", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


# ---------------------------------------------------------
# ROUTE 2: Get all saved expenses (GET)
# ---------------------------------------------------------
@app.get("/expenses", response_model=List[schemas.ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).all()


# ---------------------------------------------------------
# ROUTE 3: Delete an expense by ID (DELETE)
# ---------------------------------------------------------
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Expense not found"
        )
        
    db.delete(db_expense)
    db.commit()
    return None  # HTTP 204 requires returning no body content


# ---------------------------------------------------------
# ROUTE 4: Update an existing expense by ID (PUT)
# ---------------------------------------------------------
@app.put("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(expense_id: int, updated_expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Expense not found"
        )
        
    # Apply the structural field updates
    db_expense.title = updated_expense.title
    db_expense.amount = updated_expense.amount
    db_expense.category = updated_expense.category
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


# ---------------------------------------------------------
# ROUTE 5: Health Check (GET)
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
