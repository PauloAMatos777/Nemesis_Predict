import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from joblib import dump, load
from datetime import datetime
from backend.models import Anomaly
from sqlalchemy.orm import Session

DATA_DIR = "./data"
MODEL_PATH = "./model/lstm_model.h5"
SCALER_PATH = "./model/scaler.gz"
INPUT_STEPS = 50


def load_or_create_model(input_shape, output_dim):
    if os.path.exists(MODEL_PATH):
        return load_model(MODEL_PATH)

    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        LSTM(64),
        Dropout(0.3),
        Dense(output_dim)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model


def prepare_dataset(data: np.ndarray):
    X, y = [], []
    for i in range(len(data) - INPUT_STEPS - 1):
        X.append(data[i:i + INPUT_STEPS])
        y.append(data[i + INPUT_STEPS])
    return np.array(X), np.array(y)


def process_csv_files(db: Session):
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    if not files:
        return

    full_data = []
    for file in files:
        path = os.path.join(DATA_DIR, file)
        df = pd.read_csv(path)
        full_data.append(df)
    df_full = pd.concat(full_data).reset_index(drop=True)

    variables = df_full.columns
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df_full)

    dump(scaler, SCALER_PATH)
    X, y = prepare_dataset(data_scaled)

    model = load_or_create_model((X.shape[1], X.shape[2]), X.shape[2])
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)
    model.save(MODEL_PATH)

    last_seq = data_scaled[-INPUT_STEPS:]
    pred = model.predict(last_seq.reshape(1, INPUT_STEPS, X.shape[2]))[0]
    true = data_scaled[-1]

    diff = np.abs(pred - true)
    threshold = np.mean(diff) + 2 * np.std(diff)

    for i, d in enumerate(diff):
        is_anomaly = d > threshold
        if is_anomaly:
            anomaly = Anomaly(
                timestamp=datetime.utcnow(),
                variable=variables[i],
                anomaly_score=float(d),
                threshold=float(threshold),
                is_anomaly=True
            )
            db.add(anomaly)
    db.commit()


