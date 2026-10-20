from pydantic import BaseModel
from datetime import datetime

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
