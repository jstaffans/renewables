from datetime import datetime, timedelta
import pandas as pd


def _truncate_datetime(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def hour_range(day):
    start_midnight = _truncate_datetime(day)
    hour = start_midnight
    while hour < start_midnight + timedelta(days=1):
        yield hour
        hour = hour + timedelta(hours=1)


def hour_now():
    return datetime.utcnow().replace(minute=0, second=0, microsecond=0)


def full_hour_series(start, end, resolution, min_hours=1):
    seconds = pd.Timedelta(resolution).total_seconds()
    time_delta = end - start
    full_hour_periods = time_delta.floor("1h").total_seconds() / seconds
    full_hour_periods = max((min_hours * 60 * 60) / seconds, full_hour_periods)
    return pd.date_range(start, periods=full_hour_periods, freq=resolution)
