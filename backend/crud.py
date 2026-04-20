# DB operations
from sqlalchemy.orm import Session
from backend.models import Anomaly, Order
from backend.schemas import AnomalyCreate, OrderCreate
from sqlalchemy import func, desc
from collections import defaultdict
from datetime import datetime, timedelta

def create_anomaly(db: Session, anomaly: AnomalyCreate):
    db_anomaly = Anomaly(**anomaly.dict())
    db.add(db_anomaly)
    db.commit()
    db.refresh(db_anomaly)
    return db_anomaly

def list_anomalies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Anomaly).offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def list_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()

# Anomalias e ordens por dia
def get_events_by_day(db: Session, days: int = 60):
    cutoff = datetime.utcnow() - timedelta(days=days)

    anomalies = db.query(
        func.date(Anomaly.timestamp).label("day"),
        func.count().label("count")
    ).filter(
        Anomaly.timestamp >= cutoff
    ).group_by(
        func.date(Anomaly.timestamp)
    ).all()

    orders = db.query(
        Order.start_date.label("day"),
        func.count().label("count")
    ).filter(
        Order.start_date >= cutoff
    ).group_by(
        Order.start_date
    ).all()

    return anomalies, orders

# Ranking de variáveis por anomalias
def get_variable_ranking(db: Session, top_n: int = 10):
    return db.query(
        Anomaly.variable,
        func.count().label("count")
    ).filter(
        Anomaly.is_anomaly == True
    ).group_by(
        Anomaly.variable
    ).order_by(desc("count")).limit(top_n).all()