from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])

# ---------------------------------------------------------
# GET ALL CATEGORIES (GET /categories)
# ---------------------------------------------------------
@router.get("", response_model=List[schemas.CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Category).filter(models.Category.user_id == current_user.id).all()


# ---------------------------------------------------------
# CREATE NEW CATEGORY (POST /categories)
# ---------------------------------------------------------
@router.post("", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if category name already exists for this specific user
    existing = db.query(models.Category).filter(
        models.Category.user_id == current_user.id,
        models.Category.name.ilike(category.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    db_category = models.Category(
        name=category.name,
        type=category.type,
        color=category.color,
        user_id=current_user.id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category