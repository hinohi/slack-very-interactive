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

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base(bind=engine)
session = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=True),
)


class KVS(Base):
    __tablename__ = 'kvs'
    kvs_id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    key = Column(String(100), nullable=False)
    value = Column(String(10000), nullable=True)

    @classmethod
    def iter_column(cls):
        for col in cls.__mapper__.columns:
            yield col

    def export_dict(self):
        dic = {}
        for col in self.iter_column():
            col_name = col.name
            dic[col_name] = getattr(self, col_name)
        return dic


Base.metadata.create_all()
