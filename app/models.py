from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Leader(Base):
    __tablename__ = "leaders"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    rank = Column(Integer, nullable=False, default=1)
    player_name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    player_url = Column(String, nullable=True)
    scrape_time = Column(DateTime, default=datetime.utcnow, nullable=False)
