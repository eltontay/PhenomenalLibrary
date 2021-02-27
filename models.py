from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import *

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(40))
    password = Column(VARCHAR(40))
    first_name = Column(String)
    last_name = Column(String)
    address1 = Column(VARCHAR(40))
    address2 = Column(VARCHAR(40))
    postal_code = Column(Integer)
    