from sqlalchemy import Column, Integer, String

from sqlalchemy_generic_crud.models.base import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
