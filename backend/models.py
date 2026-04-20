from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from backend.database import Base

# SQLAlchemy Models
class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    variable = Column(String)
    anomaly_score = Column(Float)
    threshold = Column(Float)
    is_anomaly = Column(Boolean)
    observation = Column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    sap_order_id = Column(String)
    short_text = Column(String)
    equipment = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

# Pydantic Schemas
class AnomalyCreate(BaseModel):
    timestamp: datetime
    variable: str
    anomaly_score: float
    threshold: float
    is_anomaly: bool
    observation: str = None

class OrderCreate(BaseModel):
    sap_order_id: str
    short_text: str
    equipment: str
    start_date: datetime
    end_date: datetime