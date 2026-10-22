from fastapi import FastAPI
from app.routers import auth, expenses, analytics, categories, budgets

app = FastAPI(title="Expense Tracker")

# Register modular routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(analytics.router)
app.include_router(categories.router)
app.include_router(budgets.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}