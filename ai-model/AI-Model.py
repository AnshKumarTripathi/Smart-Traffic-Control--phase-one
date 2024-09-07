import numpy as np
import pandas as pd

# Set the random seed for reproducibility
np.random.seed(42)

# Number of samples
n_samples = 5000

# Feature: Number of vehicles
vehicle_count = np.random.randint(0, 50, n_samples)

# Label: Duration of green light (in seconds)
green_light_duration = np.random.normal(2, 0.5 ,n_samples) * vehicle_count + np.random.randint(1, 5, n_samples)

# Create a DataFrame
data = pd.DataFrame({
    'vehicle_count': vehicle_count,
    'green_light_duration': green_light_duration
})

# Save the dataset to a CSV file (optional)
data.to_csv('traffic_data_conditioned_random.csv', index=False)

# Load the modified dataset
data = pd.read_csv('traffic_data_conditioned_random.csv')

# Display the first few rows
print(data.head(10))

# The rest of the process remains the same as before
# Split the data, train the model, and evaluate it as usual
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Split the data into features (X) and label (y)
X = data[['vehicle_count']]
y = data['green_light_duration']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Initialize the model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R^2 Score: {r2}")

# Visualize the predictions
import matplotlib.pyplot as plt

plt.scatter(X_test, y_test, color='blue', label='Actual')
plt.scatter(X_test, y_pred, color='red', label='Predicted')
plt.xlabel('Number of Vehicles')
plt.ylabel('Green Light Duration (seconds)')
plt.legend()
plt.title('Actual vs. Predicted Green Light Duration')
plt.show()