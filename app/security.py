from passlib.context import CryptContext

# Tell passlib to use bcrypt for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Takes a plain text password and returns a secure, encrypted hash string."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a raw password input with the saved database hash to check if they match."""
    return pwd_context.verify(plain_password, hashed_password)
