from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from . import schemas
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from . import models
from dotenv import load_dotenv
import os
from .database import database
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError



# Load environment variables from .env file
load_dotenv()

# Secret key for JWT creation and verification, obtained from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
# Algorithm used for JWT creation and verification
ALGORITHM = "HS256"
# Access token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CryptContext instance for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2PasswordBearer instance for handling bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """
    Verifies a password against a hashed password using bcrypt.
    
    Args:
        plain_password (str): The plain text password
        hashed_password (str): The hashed password
    
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hashes a password using bcrypt.
    
    Args:
        password (str): The plain text password
    
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT access token with the given data and expiration time.
    
    Args:
        data (dict): The data to include in the token
        expires_delta (timedelta, optional): The time until the token expires. If not provided, defaults to 15 minutes.
    
    Returns:
        str: The encoded JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user based on the provided JWT token.
    
    Args:
        token (str): The JWT token
        db (Session): The database session
    
    Raises:
        HTTPException: If the token is invalid or the user does not exist
    
    Returns:
        models.User: The user associated with the token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    user.is_active = True
    return user

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass



async def authenticate_user(username: str, password: str):
    query = models.users.select().where(models.users.c.username == username)
    user = await database.fetch_one(query)
    print("*************user***********",user)

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user



async def get_user_by_username(username: str):
    """
    Fetches a user from the database using their username.

    Args:
        username (str): The username of the user

    Returns:
        User: SQLAlchemy User object
    """
    query = select([models.users]).where(models.users.c.username == username)
    return await database.fetch_one(query)