#!/usr/bin/env python3
"""
Script to create an admin user and initialize the API key pool.
This script connects to the database and creates a real admin user.
"""

import argparse
import os
import sys
import secrets
import datetime
from getpass import getpass
from typing import Optional

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database and models
from backend.app.database.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.group import Group, UserGroup
from backend.app.core.security import get_password_hash
from backend.app.core.config import settings
from cryptography.fernet import Fernet

def create_admin_user(
    username: str, 
    password: str, 
    email: Optional[str] = None,
    generate_token: bool = False,
    jwt_secret: Optional[str] = None
) -> User:
    """Create an admin user in the database."""
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return existing_user
            
        # Get admin group, create if not exists
        admin_group = db.query(Group).filter(Group.name == "admin").first()
        if not admin_group:
            admin_group = Group(
                name="admin",
                description="Administrator group with full permissions"
            )
            db.add(admin_group)
            db.commit()
            db.refresh(admin_group)
            print("Created admin group")
        
        # Create new admin user
        email = email or f"{username}@example.com"  # Default email if not provided
        hashed_password = get_password_hash(password)
        
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            created_at=datetime.datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Add user to admin group
        user_group = UserGroup(user_id=new_user.id, group_id=admin_group.id)
        db.add(user_group)
        db.commit()
        
        print(f"Successfully created admin user: {username}")
        
        # Generate JWT token if requested
        if generate_token and jwt_secret:
            from jose import jwt
            token_data = {
                "sub": str(new_user.id),
                "username": username,
                "role": "admin",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            token = jwt.encode(token_data, jwt_secret, algorithm="HS256")
            print(f"\nGenerated admin JWT token: {token}")
            print("Use this token for authentication in the Authorization header:")
            print(f"Authorization: Bearer {token}")
        
        return new_user
    
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        raise
    finally:
        db.close()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Create admin user and initialize API key pool')
    parser.add_argument('--username', type=str, help='Admin username')
    parser.add_argument('--password', type=str, help='Admin password (will prompt if not provided)')
    parser.add_argument('--email', type=str, help='Admin email address')
    parser.add_argument('--jwt-secret', type=str, help='JWT secret for token generation')
    parser.add_argument('--generate-token', action='store_true', help='Generate a JWT token for the user')
    args = parser.parse_args()

    # Get username
    username = args.username or input("Admin username: ")

    # Get password securely (unless provided in args)
    password = args.password
    if not password:
        password = getpass("Admin password: ")
        password_confirm = getpass("Confirm password: ")
        if password != password_confirm:
            print("Passwords do not match. Exiting.")
            sys.exit(1)

    # Get email 
    email = args.email

    # JWT secret key
    jwt_secret = args.jwt_secret or os.getenv("JWT_SECRET", settings.JWT_SECRET)

    # Create the admin user
    create_admin_user(
        username=username, 
        password=password, 
        email=email,
        generate_token=args.generate_token,
        jwt_secret=jwt_secret
    )

    # Generate an encryption key for API keys
    encryption_key = Fernet.generate_key()
    print(f"\nGenerated encryption key: {encryption_key.decode()}")
    print("Add this to your .env file as API_KEY_ENCRYPTION_KEY")

    print("\nSetup complete!")
    print("\nMake sure to set these environment variables if not already set:")
    print(f"API_KEY_ENCRYPTION_KEY={encryption_key.decode()}")
    print(f"JWT_SECRET={jwt_secret}")
    print("VERIFY_API_KEYS=true # if you want to verify keys with providers")

if __name__ == "__main__":
    main() 