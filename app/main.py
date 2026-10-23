from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.expenses import router as expenses_router
from app.routers.analytics import router as analytics_router
from app.routers.categories import router as categories_router
from app.routers.budgets import router as budgets_router

app = FastAPI(title="Expense Tracker")

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(expenses_router)
app.include_router(analytics_router)
app.include_router(categories_router)
app.include_router(budgets_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}