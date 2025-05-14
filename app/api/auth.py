from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
import jwt
from datetime import datetime, timedelta
import json

from app.core.config import settings
from app.services.user_service import register_user, authenticate_user, get_user

router = APIRouter(prefix="/auth", tags=["auth"])

def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: Dict[str, Any]):
    """
    Register a new user using file-based storage
    """
    if not user_data.get("email") or not user_data.get("password"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    success = register_user(user_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return {"message": "User registered successfully"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint to get access token
    """
    email = form_data.username
    password = form_data.password
    
    if not authenticate_user(email, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create and return access token
    token = create_access_token({"sub": email})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str) -> Dict[str, Any]:
    """
    Validate token and return current user
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    
    user = get_user(email)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    
    return user 