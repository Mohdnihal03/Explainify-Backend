from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get DATABASE_URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for development if not set
if not SQLALCHEMY_DATABASE_URL:
    # Use a default or raise an error. For now, we'll print a warning.
    # The user might need to set this in their .env
    print("WARNING: DATABASE_URL not found in .env. Please add it.")
    # Example format: postgresql://user:password@localhost/dbname
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Nihal%40456@localhost/explainify"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
