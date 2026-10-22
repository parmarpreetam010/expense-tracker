from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List
# This defines what data we NEED when someone creates a new expense
class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str

# This defines what data our app will SEND BACK to the user
class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    date: datetime

    class Config:
        from_attributes = True

from pydantic import EmailStr, BaseModel # EmailStr ensures incoming data is a valid email format

# Schema 1: What data we NEED when a user signs up
class UserCreate(BaseModel):
    email: str # Tip: If you want strict validation, you can change this to EmailStr later
    password: str

# Schema 2: What data our app will securely SEND BACK to the user profile
class UserResponse(BaseModel):
    id: int
    email: str
    date_created: Optional[datetime] = None # Matches our model timestamp field

    class Config:
        from_attributes = True
# Schema 3: What the server sends back after a successful login
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema 4: The structural data stored inside the decrypted token
class TokenData(BaseModel):
    user_id: Optional[int] = None

# Schema 5: Layout for category-wise breakdowns
class CategorySpend(BaseModel):
    category: str
    total_amount: float

# Schema 6: Layout for the full financial dashboard summary
class MonthSummaryResponse(BaseModel):
    total_spending: float
    category_breakdown: List[CategorySpend]

    class Config:
        from_attributes = True

