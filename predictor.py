import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Sample resource usage data (e.g., CPU usage percentage over time)
data = [60, 65, 70, 75, 80, 85, 75, 70, 65, 60, 55, 50, 45, 50, 55, 60, 65, 70, 75, 80]
data = np.array(data)

# Scaling the data between 0 and 1
scaler = MinMaxScaler(feature_range=(0, 1))
data_scaled = scaler.fit_transform(data.reshape(-1, 1))

# Prepare data for LSTM (time series data with a look-back window)
def create_dataset(data, look_back=3):
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i:i + look_back, 0])
        y.append(data[i + look_back, 0])
    return np.array(X), np.array(y)

look_back = 3
X, y = create_dataset(data_scaled, look_back)

# Reshape input to be [samples, time steps, features]
X = np.reshape(X, (X.shape[0], look_back, 1))

# Define the LSTM model
model = Sequential([
    LSTM(50, return_sequences=False, input_shape=(look_back, 1)),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X, y, epochs=50, batch_size=1, verbose=1)

# Predict the next resource usage
last_sequence = data_scaled[-look_back:]
last_sequence = np.reshape(last_sequence, (1, look_back, 1))
predicted_value = model.predict(last_sequence)
predicted_value = scaler.inverse_transform(predicted_value)

print(f"Predicted next resource usage: {predicted_value[0][0]:.2f}%")

# Auto-scaling decision logic
scale_up_threshold = 80  # Example threshold to scale up
scale_down_threshold = 50  # Example threshold to scale down

if predicted_value[0][0] > scale_up_threshold:
    print("Action: Scale up resources.")
elif predicted_value[0][0] < scale_down_threshold:
    print("Action: Scale down resources.")
else:
    print("Action: Maintain current resources.")

# Plot the original data and prediction
plt.plot(data, label='Original Data')
plt.axhline(predicted_value[0][0], color='r', linestyle='--', label='Predicted Next Value')
plt.legend()
plt.title('Resource Usage Prediction')
plt.show()
