from fastapi import FastAPI
from app.routers import auth, expenses, analytics

app = FastAPI(title="Expense Tracker")

# Include the modular routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(analytics.router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}