from fastapi import FastAPI
import pandas as pd
from darts import TimeSeries
from darts.models import RegressionModel

from util import extend_covariates

app = FastAPI()

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
                                             value_cols=['avg_temp', 'avg_humidity', 'total_precip', 'masked_area',
                                                         'change'],
                                             freq='W')

@app.get("/forecast_dam_level")
def forecast_dam_level(n_weeks: int = 12):
    """
    API endpoint to forecast the dam's water level.

    - Reads the dataset dynamically.
    - Loads the trained regression model.
    - Predicts the next 'n_weeks' of 'available_useful_volume'.
    - Returns forecasted values as JSON.

    Parameters:
    - n_weeks: Number of weeks to forecast (default: 12, range: 1-52)

    Returns:
    - JSON response with timestamps and forecasted dam levels.
    """
    from darts.models import RegressionModel

    # Load trained model
    loaded_model = RegressionModel.load("multivar_regression_forecaster.pkl")

    # Compute required start date for covariates
    required_start_pred = target_series.end_time() - pd.Timedelta(weeks=12)

    # Extend the covariates forward to match the forecast horizon
    cov_extended = extend_covariates(covariate_series, required_start_pred)

    # Ensure covariates cover the future forecast period
    future_dates = pd.date_range(start=target_series.end_time() + pd.Timedelta(weeks=1),
                                 periods=n_weeks, freq='W')

    # Use the last known covariate values to fill in future missing covariates
    last_cov_values = cov_extended.pd_dataframe().iloc[-1]
    future_cov_df = pd.DataFrame([last_cov_values] * len(future_dates), index=future_dates,
                                 columns=cov_extended.columns)

    # Convert to TimeSeries
    future_cov_series = TimeSeries.from_dataframe(future_cov_df, freq='W')

    # Append future covariates to existing covariates
    full_cov_series = cov_extended.append(future_cov_series)

    # Generate forecast
    forecast = loaded_model.predict(n=n_weeks, past_covariates=full_cov_series, verbose=True, show_warnings=False)

    # Convert forecast to JSON format
    forecast_df = forecast.pd_dataframe().reset_index()
    forecast_df.columns = ["timestamp", "forecasted_available_useful_volume"]

    return forecast_df.to_dict(orient="records")


# Run the application with Uvicorn (recommended for FastAPI)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="debug")