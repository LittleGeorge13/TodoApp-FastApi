from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connecting to SQLite
# SQLACHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# engine = create_engine(SQLACHEMY_DATABASE_URL, connect_args={ 'check_same_thread': False })

SQLACHEMY_DATABASE_URL = 'postgresql://postgres:admin@localhost/TodoApplicationDatabase'
engine = create_engine(SQLACHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()