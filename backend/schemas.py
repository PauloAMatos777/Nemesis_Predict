# (optional) Input/Output schemas
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class AnomalyCreate(BaseModel):
    timestamp: datetime
    equipment: str
    system: Optional[str]
    variable: str
    real_value: float
    predicted_value: float
    anomaly_score: float
    threshold: float
    is_anomaly: bool
    observation: Optional[str] = None
    order_id: Optional[int] = None

class AnomalyOut(AnomalyCreate):
    id: int

class OrderCreate(BaseModel):
    sap_order_id: Optional[str]
    equipment: str
    short_text: str
    start_date: date
    end_date: date

class OrderOut(OrderCreate):
    id: int
