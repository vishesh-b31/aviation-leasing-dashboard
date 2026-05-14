import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Generate training data
np.random.seed(42)
rows = []
for _ in range(2000):
    age = np.random.randint(0, 25)
    utilisation = np.random.uniform(0.6, 1.0)
    cycles = age * np.random.uniform(1200, 1800)
    market_condition = np.random.uniform(0.8, 1.2)
    base = np.random.choice([108, 130, 80, 317, 292])
    value = base * ((1 - 0.05) ** age) * utilisation * market_condition
    value += np.random.normal(0, 5)
    rows.append([age, utilisation, cycles, market_condition, base, value])

df = pd.DataFrame(rows, columns=["age", "utilisation", "cycles", "market", "base_value", "value"])

# Train the model
X = df[["age", "utilisation", "cycles", "market", "base_value"]]
y = df["value"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = GradientBoostingRegressor(n_estimators=200, max_depth=4)
model.fit(X_train, y_train)

print("MAE:", mean_absolute_error(y_test, model.predict(X_test)))

# Save the model
joblib.dump(model, "value_model.pkl")
print("Model saved successfully!")