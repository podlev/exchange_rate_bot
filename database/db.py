from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///db.sqlite', echo=False)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    created_date = Column(DateTime(), default=datetime.now)
    subscribes = relationship('Subscribe', back_populates="user")
    types = relationship('SubscribeType', back_populates="user")



class SubscribeType(Base):
    __tablename__ = 'subscribetypes'
    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    delay = Column(Integer, nullable=True)
    delta = Column(Float, nullable=True)
    user = relationship('User', back_populates="types")

    def __repr__(self):
        return f'Подписка пользователя {self.user_id}: ({self.type}, {self.delay}, {self.delta})'

    def __str__(self):
        return f'Подписка пользователя {self.user_id}: тип {self.type}, задержка {self.delay} изменение {self.delta}'



class Subscribe(Base):
    __tablename__ = 'subscribe'
    code = Column(String, primary_key=True)
    name = Column(String)
    nominal = Column(Integer)
    value = Column(Float)
    previous = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    created_date = Column(DateTime(), default=datetime.now)
    user = relationship('User', back_populates="subscribes")


Base.metadata.create_all(engine)
