import csv
import io
from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/expenses", tags=["Expenses"])

from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=schemas.PaginatedExpenseResponse)
def get_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    start_date: Optional[datetime] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(default=None, description="End date (YYYY-MM-DD)"),
    sort_by: Literal["date", "amount"] = Query(default="date", description="Sort by date or amount"),
    order: Literal["asc", "desc"] = Query(default="desc", description="Sort direction")
):
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    if category:
        query = query.filter(models.Expense.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    total_records = query.count()

    sort_column = models.Expense.amount if sort_by == "amount" else models.Expense.date
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(sort_column))

    expenses = query.offset(offset).limit(limit).all()

    return {
        "total_records": total_records,
        "limit": limit,
        "offset": offset,
        "data": expenses
    }


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
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
# CSV EXPORT ENDPOINT: Stream filtered expenses as CSV
# ---------------------------------------------------------
@router.get("/export")
def export_expenses_csv(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    start_date: Optional[datetime] = Query(default=None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(default=None, description="Filter up to date (YYYY-MM-DD)")
):
    # 1. Query expenses strictly scoped to current user
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    # 2. Apply optional filters
    if category:
        query = query.filter(models.Expense.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    expenses = query.order_by(desc(models.Expense.date)).all()

    # 3. Create an in-memory string buffer and write CSV records
    output = io.StringIO()
    writer = csv.writer(output)

    # Write column headers
    writer.writerow(["ID", "Title", "Amount", "Category", "Date"])

    # Write data rows
    for item in expenses:
        formatted_date = item.date.strftime("%Y-%m-%d %H:%M:%S") if item.date else ""
        writer.writerow([item.id, item.title, item.amount, item.category, formatted_date])

    # 4. Reset stream cursor to beginning
    output.seek(0)

    # 5. Return as downloadable file attachment stream
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"expenses_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

    @router.put("/{expense_id}", response_model=schemas.ExpenseResponse, tags=["Expenses"])
def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id)
        .first()
    )
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    expense.title = expense_update.title
    expense.amount = expense_update.amount
    expense.category = expense_update.category
    if expense_update.date:
        expense.date = expense_update.date

    db.commit()
    db.refresh(expense)
    return expense