import os
import pandas as pd
from datetime import datetime, timedelta
from app.model import csv_to_pd

#
# Helpers for creating Pandas DataFrames for test purposes
#


def _csv(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def _set_timestamp(df, t):
    assert df.shape[0] == 1

    df.reset_index(inplace=True)
    df.ix[0, "timestamp"] = t
    return df.set_index("timestamp")


def single_generation_report():
    return csv_to_pd(_csv("generation_2018_single.csv"))


def timestamped_single_generation_report(t):
    reading = single_generation_report()
    reading = _set_timestamp(reading, t)
    return reading


def single_weather_forecast():
    return csv_to_pd(_csv("weather_2018_single.csv"))


def timestamped_single_weather_forecast(t):
    forecast = single_weather_forecast()
    forecast = _set_timestamp(forecast, t)
    return forecast


def current_weather_forecast():
    """
    Returns a dummy forecast for today and tomorrow (all 48 hours).
    """
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp_series = pd.date_range(midnight, periods=48, freq="1h")
    forecast = pd.DataFrame(index=timestamp_series)
    forecast["temperature"] = 20.0
    forecast["wind_speed"] = 0.0
    forecast["cloud_cover"] = 0.0
    forecast["pressure"] = 1024.0
    return forecast
