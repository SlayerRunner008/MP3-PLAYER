from sqlalchemy import Column, Integer, String
from config.database import Base

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    length = Column(Integer, nullable=True)
    url = Column(String, nullable=True)