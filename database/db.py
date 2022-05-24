from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///db.sqlite', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    created_date = Column(DateTime(), default=datetime.now)
    subscribes = relationship('Subscribe', backref="user")


class Subscribe(Base):
    __tablename__ = 'subscribe'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    value = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_date = Column(DateTime(), default=datetime.now)


Base.metadata.create_all(engine)
