import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def fetch_weather_data(lat, lon):
    # Define the start and end date (past 4 years)
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=(3 * 365) + 60)

    # Convert to string format (YYYY-MM-DD)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Open-Meteo API URL (fetch daily data)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date_str}&end_date={end_date_str}&daily=temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean&timezone=Europe/Sofia"

    # Make the API request
    response = requests.get(url)
    data = response.json()

    # Extract relevant fields
    dates = data["daily"]["time"]
    temp_avg = data["daily"]["temperature_2m_mean"]
    humidity = data["daily"]["relative_humidity_2m_mean"]
    precipitation = data["daily"]["precipitation_sum"]

    # Create a Pandas DataFrame
    df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Avg Temperature (°C)": temp_avg,
        "Avg Humidity (%)": humidity,
        "Total Precipitation (mm)": precipitation
    })

    # Convert daily data to weekly averages/sums
    df.set_index("Date", inplace=True)
    weekly_data = df.resample("W").agg({
        "Avg Temperature (°C)": "mean",
        "Avg Humidity (%)": "mean",
        "Total Precipitation (mm)": "sum"
    })

    return weekly_data


def plot_weather_data(df):
    plt.figure(figsize=(12, 6))

    # Temperature Plot
    plt.subplot(3, 1, 1)
    plt.plot(df.index, df["Avg Temperature (°C)"], color="red", label="Avg Temperature (°C)")
    plt.ylabel("°C")
    plt.title("Weekly Average Temperature")
    plt.legend()

    # Humidity Plot
    plt.subplot(3, 1, 2)
    plt.plot(df.index, df["Avg Humidity (%)"], color="blue", label="Avg Humidity (%)")
    plt.ylabel("%")
    plt.title("Weekly Average Humidity")
    plt.legend()

    # Precipitation Plot
    plt.subplot(3, 1, 3)
    plt.bar(df.index, df["Total Precipitation (mm)"], color="green", label="Total Precipitation (mm)")
    plt.ylabel("mm")
    plt.title("Weekly Total Precipitation")
    plt.legend()

    plt.tight_layout()
    plt.show()


# Example: Fetch data for Sofia, Bulgaria
latitude = 42.6977
longitude = 23.3219
weekly_weather = fetch_weather_data(latitude, longitude)

weekly_weather.to_csv("weekly_weather_data.csv")

plot_weather_data(weekly_weather)