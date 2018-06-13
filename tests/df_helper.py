import os
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
