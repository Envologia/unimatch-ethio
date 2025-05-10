from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from .models import Base

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database."""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session."""
    return Session() 