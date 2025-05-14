import os
import json
from datetime import datetime
from typing import Dict, Any

# Directory to store user files
USER_DATA_DIR = os.path.join("data", "users")
os.makedirs(USER_DATA_DIR, exist_ok=True)

def register_user(user_data: Dict[str, Any]) -> bool:
    """
    Register a new user by storing their information in a file
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        bool: True if successful, False otherwise
    """
    email = user_data.get("email")
    if not email:
        return False
    
    # Create user directory
    user_dir = os.path.join(USER_DATA_DIR, email)
    if os.path.exists(user_dir):
        return False  # User already exists
    
    os.makedirs(user_dir, exist_ok=True)
    os.makedirs(os.path.join(user_dir, "uploads"), exist_ok=True)
    
    # Store user data
    user_data["created_at"] = datetime.now().isoformat()
    user_data["uploads"] = []
    
    user_file = os.path.join(user_dir, "profile.json")
    with open(user_file, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    return True

def get_user(email: str) -> Dict[str, Any]:
    """
    Get user data
    
    Args:
        email: User email
        
    Returns:
        dict: User data or empty dict if not found
    """
    user_file = os.path.join(USER_DATA_DIR, email, "profile.json")
    if not os.path.exists(user_file):
        return {}
    
    with open(user_file, 'r') as f:
        return json.load(f)

def authenticate_user(email: str, password: str) -> bool:
    """
    Authenticate a user
    
    Args:
        email: User email
        password: User password
        
    Returns:
        bool: True if authenticated, False otherwise
    """
    user_data = get_user(email)
    if not user_data:
        return False
    
    return user_data.get("password") == password

def add_upload_record(email: str, upload_data: Dict[str, Any]) -> bool:
    """
    Add an upload record to the user's profile
    
    Args:
        email: User email
        upload_data: Upload data
        
    Returns:
        bool: True if successful, False otherwise
    """
    user_data = get_user(email)
    if not user_data:
        return False
    
    upload_data["timestamp"] = datetime.now().isoformat()
    
    # Add to uploads array
    user_data["uploads"].append(upload_data)
    
    # Update profile
    user_file = os.path.join(USER_DATA_DIR, email, "profile.json")
    with open(user_file, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    return True 