from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import engine, SessionLocal, Base
from backend import crud, models, schemas
from backend.models import Anomaly, Order  # Corrigido
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from backend.ml_service import process_csv_files
from datetime import datetime, timedelta
import os


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: process_csv_files(db=SessionLocal()),
        trigger="interval",
        minutes=5,
        id="ml_routine",
        replace_existing=True
    )
    scheduler.start()

@app.post("/anomalias")
def create_anomaly(anomaly: models.AnomalyCreate, db: Session = Depends(get_db)):
    return crud.create_anomaly(db, anomaly)

@app.get("/anomalias")
def list_anomalies(db: Session = Depends(get_db)):
    return crud.get_anomalies(db)

@app.post("/ordens")
def create_order(order: models.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order)

@app.get("/ordens")
def list_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)

@app.get("/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    recent_anomalies = db.query(Anomaly).order_by(Anomaly.timestamp.desc()).limit(200).all()
    detection_series = [
        {
            "timestamp": a.timestamp.isoformat(),
            "indice": a.anomaly_score,
            "limiar": a.threshold,
            "is_anomaly": a.is_anomaly
        } for a in sorted(recent_anomalies, key=lambda x: x.timestamp)
    ]

    anomalies_by_day, orders_by_day = crud.get_events_by_day(db)
    anomalies_count = {str(a.day): a.count for a in anomalies_by_day}
    orders_count = {str(o.day): o.count for o in orders_by_day}
    days = sorted(set(anomalies_count.keys()).union(set(orders_count.keys())))

    events = []
    for d in days:
        events.append({
            "day": d,
            "anomalies": anomalies_count.get(d, 0),
            "orders": orders_count.get(d, 0)
        })

    ranking = crud.get_variable_ranking(db)
    ranking_data = [{"variable": r.variable, "count": r.count} for r in ranking]

    recent_anomalies_list = [
        {
            "timestamp": a.timestamp.isoformat(),
            "variable": a.variable,
            "validated": False,
            "observation": a.observation or "Não avaliado"
        } for a in recent_anomalies
    ]

    recent_orders = db.query(Order).order_by(Order.start_date.desc()).limit(10).all()
    orders_list = [
        {
            "sap_order_id": o.sap_order_id,
            "short_text": o.short_text,
            "equipment": o.equipment,
            "start_date": o.start_date.isoformat(),
            "end_date": o.end_date.isoformat()
        } for o in recent_orders
    ]

    return JSONResponse({
        "deteccao_anomalias": detection_series,
        "eventos_por_dia": events,
        "ranking_variaveis": ranking_data,
        "historico_anomalias": recent_anomalies_list,
        "historico_ordens": orders_list
    })
