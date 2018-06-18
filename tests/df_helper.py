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


def generation_report_range(start, end):
    df = pd.DataFrame()

    t = start
    while t <= end:
        df = df.append(timestamped_single_generation_report(t))
        t = t + timedelta(hours=1)

    return df


def single_weather_forecast():
    return csv_to_pd(_csv("weather_2018_single.csv"))


def timestamped_single_weather_forecast(t):
    forecast = single_weather_forecast()
    forecast = _set_timestamp(forecast, t)
    return forecast


def weather_report_range(start, end):
    h = start
    weather = pd.DataFrame()
    while h < end:
        weather = weather.append(timestamped_single_weather_forecast(h))
        h = h + timedelta(hours=1)
    return weather
