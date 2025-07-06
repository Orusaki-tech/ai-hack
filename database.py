from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL. SQLite will create a file named 'market_data.db'
SQLALCHEMY_DATABASE_URL = "sqlite:///./market_data.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of the SessionLocal class will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models to inherit from
Base = declarative_base()

# Helper function to create the database tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)