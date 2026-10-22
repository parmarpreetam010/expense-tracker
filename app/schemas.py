from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================
# EXPENSE SCHEMAS
# ==========================================

# What data is required to create a new expense
class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str


# What data the app returns for a single expense record
class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    date: datetime

    model_config = ConfigDict(from_attributes=True)


# Wrapper for paginated results (must be defined AFTER ExpenseResponse)
class PaginatedExpenseResponse(BaseModel):
    total_records: int
    limit: int
    offset: int
    data: List[ExpenseResponse]

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# USER & AUTH SCHEMAS
# ==========================================

# Data required when a user registers
class UserCreate(BaseModel):
    email: str
    password: str


# Data returned for user profiles
class UserResponse(BaseModel):
    id: int
    email: str
    date_created: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Response after successful authentication
class Token(BaseModel):
    access_token: str
    token_type: str


# Decoded token payload structure
class TokenData(BaseModel):
    user_id: Optional[int] = None


# ==========================================
# ANALYTICS SCHEMAS
# ==========================================

class CategorySpend(BaseModel):
    category: str
    total_amount: float


class MonthSummaryResponse(BaseModel):
    total_spending: float
    category_breakdown: List[CategorySpend]

    model_config = ConfigDict(from_attributes=True)