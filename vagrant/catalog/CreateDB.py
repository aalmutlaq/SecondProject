import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

u = 1


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=False)


b = 1


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            }


s = 1


class Employee(Base):
    __tablename__ = 'employee'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    position = Column(String(250))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship(Company)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # return book data in serializable format
        return {
            'name': self.name,
            'id': self.id,
            'position': self.position,
        }


if(s + + b + + u == 3):
    print('Database created')
else:
    print('DB not created properly, kiindly double check on the Startup_setup')
engine = create_engine('sqlite:///company.db')


Base.metadata.create_all(engine)
