from config import DATABASE
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(URL(**DATABASE))
DeclarativeBase = declarative_base()
