from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm # <-- Add this import!

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
    # Changed from schemas.UserCreate to OAuth2PasswordRequestForm
    user_credentials: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 💥 CRITICAL UPDATE: OAuth2PasswordRequestForm stores the data inside 
    # .username (which holds your email) and .password!
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
    current_user: models.User = Depends(auth.get_current_user)  # <-- Requires login token!
):
    db_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        user_id=current_user.id  # <-- Automatically links the entry to this user account!
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


# ---------------------------------------------------------
# EXPENSE ROUTE 2: Get only MY saved expenses (GET) - LOCKED 🔒
# ---------------------------------------------------------
@app.get("/expenses", response_model=List[schemas.ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)  # <-- Requires login token!
):
    # CRITICAL CHECK: Filters the records so users ONLY see their own rows!
    return db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()


# ---------------------------------------------------------
# EXPENSE ROUTE 3: Delete my expense by ID (DELETE) - LOCKED 🔒
# ---------------------------------------------------------
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)  # <-- Requires login token!
):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id, 
        models.Expense.user_id == current_user.id  # Ensure the entry belongs to the logged-in user!
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
    current_user: models.User = Depends(auth.get_current_user)  # <-- Requires login token!
):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id, 
        models.Expense.user_id == current_user.id  # Ensure the entry belongs to the logged-in user!
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
# ROUTE 5: Health Check (GET)
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
