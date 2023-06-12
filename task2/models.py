from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    access_token = Column(String)

    def __init__(self, name, access_token):
        self.name = name
        self.access_token = access_token


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    filename = Column(String)
    uuid = Column(String)

    def __init__(self, user_id, filename, uuid):
        self.user_id = user_id
        self.filename = filename
        self.uuid = uuid
