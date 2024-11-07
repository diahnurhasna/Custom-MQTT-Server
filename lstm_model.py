import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from influxdb import InfluxDBClient
import config
import pickle

def load_data():
    # Connect to InfluxDB
    client = InfluxDBClient(
        host=config.INFLUXDB_HOST,
        port=config.INFLUXDB_PORT,
        database=config.INFLUXDB_DATABASE
    )
    # Load historical data
    results = client.query('SELECT pub_count, sub_count FROM mqtt_message_count')
    data = list(results.get_points())
    return data

def preprocess_data(data):
    pub_counts = np.array([point['pub_count'] for point in data])
    sub_counts = np.array([point['sub_count'] for point in data])

    scaler = MinMaxScaler()
    pub_counts = scaler.fit_transform(pub_counts.reshape(-1, 1))
    sub_counts = scaler.fit_transform(sub_counts.reshape(-1, 1))
    
    # Save scaler for later use in prediction
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    
    # Create sequences for LSTM
    sequence_length = 30
    X, y = [], []
    for i in range(len(pub_counts) - sequence_length):
        X.append(pub_counts[i:i + sequence_length])
        y.append(pub_counts[i + sequence_length])
    return np.array(X), np.array(y)

def build_and_train_model(X, y):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=20, batch_size=16)
    return model

if __name__ == "__main__":
    data = load_data()
    X, y = preprocess_data(data)
    model = build_and_train_model(X, y)
    model.save("mqtt_lstm_model.h5")
    print("[INFO] Model trained and saved to mqtt_lstm_model.h5")
