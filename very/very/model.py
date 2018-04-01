import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base(bind=engine)
session = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=True),
)


class SlackRequest(Base):
    __tablename__ = 'kvs'
    kvs_id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    key = Column(String(100), nullable=False)
    value = Column(String(1000), nullable=True)


Base.metadata.create_all()
