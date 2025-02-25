#!/usr/bin/env python3
"""
Script to create an admin user and initialize the API key pool.
This is a simplified placeholder - in a real implementation, this would
interact with the database directly.
"""

import argparse
import os
import sys
import json
import base64
import datetime
from jose import jwt
from cryptography.fernet import Fernet

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Parse arguments
parser = argparse.ArgumentParser(description='Create admin user and initialize API key pool')
parser.add_argument('--username', type=str, help='Admin username')
parser.add_argument('--password', type=str, help='Admin password (will prompt if not provided)')
parser.add_argument('--jwt-secret', type=str, help='JWT secret for token generation')
args = parser.parse_args()

# Get username and password
username = args.username or input("Admin username: ")
password = args.password or input("Admin password (visible): ")

# JWT secret key
jwt_secret = args.jwt_secret or os.getenv("JWT_SECRET", "dev_jwt_secret_key_change_in_production")

# Create a token with admin privileges
token_data = {
    "sub": username, 
    "role": "admin",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}

try:
    token = jwt.encode(token_data, jwt_secret, algorithm="HS256")
    print(f"\nGenerated admin JWT token: {token}")
    print("Use this token for authentication in the Authorization header:")
    print(f"Authorization: Bearer {token}")
except Exception as e:
    print(f"Error generating JWT token: {e}")

# Generate an encryption key for API keys
encryption_key = Fernet.generate_key()
print(f"\nGenerated encryption key: {encryption_key.decode()}")
print("Add this to your .env file as API_KEY_ENCRYPTION_KEY")

print("\nSetup complete!")
print(f"Admin user '{username}' created with JWT token.")
print("\nMake sure to set these environment variables:")
print(f"API_KEY_ENCRYPTION_KEY={encryption_key.decode()}")
print(f"JWT_SECRET={jwt_secret}")
print("VERIFY_API_KEYS=true # if you want to verify keys with providers") 