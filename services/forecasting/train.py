import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from darts import TimeSeries
from darts.models import RegressionModel
from darts.metrics import mape, rmse, smape
from sklearn.linear_model import LinearRegression, ARDRegression, QuantileRegressor

from util import extend_covariates

# =============================================================================
# 1. Data Preparation
# =============================================================================

# Load your DataFrame (modify path if needed)
# df = pd.read_csv("your_data.csv")

# Rename columns to simpler names (adjust if necessary)
df = pd.read_csv("Ticha-dataset.csv")

df = df.rename(columns={
    "Avg Temperature (°C)": "avg_temp",
    "Avg Humidity (%)": "avg_humidity",
    "Total Precipitation (mm)": "total_precip",
    "Masked Area (km²)": "masked_area"
})

# Ensure required columns exist
required_columns = ["timestamp", "change", "avg_temp", "avg_humidity", "total_precip", "masked_area"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found. Available columns: {df.columns.tolist()}")

# Convert timestamp to datetime and sort
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# Create TimeSeries objects
target_series = TimeSeries.from_dataframe(df, time_col='timestamp', value_cols='available_useful_volume', freq='W')
covariate_series = TimeSeries.from_dataframe(df, time_col='timestamp',
                                             value_cols=['avg_temp', 'avg_humidity', 'total_precip', 'masked_area', 'change'],
                                             freq='W')

# =============================================================================
# 2. Train/Validation Split
# =============================================================================

train_ratio = 0.8
split_point = int(len(target_series) * train_ratio)
train_target = target_series[:split_point]
val_target = target_series[split_point:]
train_cov = covariate_series[:split_point]
val_cov = covariate_series[split_point:]

# =============================================================================
# 3. Extend Validation Covariates (if needed)
# =============================================================================

# Compute required start time for covariates
required_start = val_target.start_time() - pd.Timedelta(weeks=12)

# Extend the validation covariates if necessary
val_cov = extend_covariates(val_cov, required_start)

# =============================================================================
# 4. Train a Multivariate Regression Model
# =============================================================================

# Specify lags for the target and past covariates (12 weeks)
lags_target = list(range(-12, 0))  # [-12, -11, ..., -1]
lags_cov = list(range(-12, 0))  # Same for past covariates

# Build the RegressionModel
model = RegressionModel(
    model=QuantileRegressor(),
    lags=lags_target,
    lags_past_covariates=lags_cov,
    output_chunk_length=12  # Forecast 12 weeks ahead
)

# Train the model
model.fit(series=train_target, past_covariates=train_cov)

# =============================================================================
# 5. Validation Forecast & Evaluation
# =============================================================================

# Validation Forecast & Evaluation
val_forecast = model.predict(n=len(val_target), past_covariates=val_cov, verbose=True, show_warnings=False)

# Use SMAPE instead of MAPE
val_smape = smape(val_target, val_forecast)
val_rmse = rmse(val_target, val_forecast)

print(f"Validation SMAPE: {val_smape:.2f}%")
print(f"Validation RMSE: {val_rmse:.2f}")

# Plot results
plt.figure(figsize=(12, 6))
train_target.plot(label="Train", lw=2)
val_target.plot(label="Actual Validation", lw=2)
val_forecast.plot(label="Forecast", lw=2)
plt.title("Validation Forecast for Dependent Variable's Change")
plt.xlabel("Timestamp")
plt.ylabel("Change")
plt.legend()
plt.show()

# Save model
model.save("multivar_regression_forecaster.pkl")
print("Model saved as 'multivar_regression_forecaster.pkl'.")

