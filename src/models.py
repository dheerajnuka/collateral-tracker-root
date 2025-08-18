from datetime import date
from sqlalchemy import Column, Integer, Float, String, Date
from .db import Base

class Collateral(Base):
    __tablename__ = "collateral"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(Date, default=date.today)  # "Date"
    customer_name = Column(String, nullable=False)  # "Name"
    item = Column(String, nullable=False)  # "Item Name"
    weight_grams = Column(Float, nullable=True)  # "Weight"
    principal = Column(Float, nullable=False)  # "Amount"
    interest_rate_pa = Column(Float, nullable=False)  # UI field, not used in calc
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # kept for compatibility; mirrors received_date
    status = Column(String, default="")  # "", Taken, ReWrite, Sold
    comments = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)  # "Phone Number"
    received_date = Column(Date, nullable=True)  # "Date Of Item Received" (treated as end date)
    amount_received = Column(Float, nullable=True)  # "Amount Received"
