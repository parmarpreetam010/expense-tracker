import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Load the secret connection string from your hidden .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Create the core engine that manages connections to Neon
engine = create_engine(DATABASE_URL)

# 3. Create a Session factory to easily open and close transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the base class that our future data models (tables) will inherit
Base = declarative_base()

# 5. Helper function to safely manage database connections per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
