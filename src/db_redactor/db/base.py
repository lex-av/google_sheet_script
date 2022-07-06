from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from src.db_redactor.config import DATABASE

engine = create_engine(URL(**DATABASE))
DeclarativeBase = declarative_base()
