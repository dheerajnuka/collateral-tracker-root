from datetime import date
from sqlalchemy import Column, Integer, Float, String, Date
from .db import Base

class Collateral(Base):
    __tablename__ = "collateral"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(Date, default=date.today)
    customer_name = Column(String, nullable=False)
    item = Column(String, nullable=False)
    weight_grams = Column(Float, nullable=True)
    principal = Column(Float, nullable=False)
    interest_rate_pa = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String, default="Active")
    comments = Column(String, nullable=True)
