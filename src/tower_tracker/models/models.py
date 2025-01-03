from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RunStatistics(Base):  # ignore: type
    __tablename__ = "run_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime_collected = Column(DateTime, default=datetime.utcnow, nullable=False)
    tier = Column(Integer, nullable=False)
    wave = Column(Integer, nullable=False)
    coins = Column(Float, nullable=False)
    cells = Column(Integer, nullable=False)
    time_spent = Column(Integer, nullable=False)  # in seconds
    notes = Column(String, nullable=True)
    end_of_round = Column(Boolean, default=False, nullable=False)
