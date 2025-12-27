# backend/config.py

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:ADLAB@127.0.0.1:5432/alshifa_db"
)

# JWT Configuration
SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "alshifa_super_secret_key_change_this_in_prod"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours = 1440 minutes

# CORS Configuration
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# Database Pool Configuration
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 40
DB_POOL_PRE_PING = True
