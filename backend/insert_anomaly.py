from backend.database import SessionLocal
from backend.models import Anomaly
from datetime import datetime

session = SessionLocal()

nova_anomalia = Anomaly(
    timestamp=datetime.utcnow(),
    equipment="IDF3",
    system="Sistema A",
    variable="Nível do Tanque",
    real_value=0.25,
    predicted_value=0.85,
    anomaly_score=0.6,
    threshold=0.4,
    is_anomaly=True
)

session.add(nova_anomalia)
session.commit()
session.close()
