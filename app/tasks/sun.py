import pandas as pd
from datetime import timedelta
from astral import Astral

def _truncate_datetime(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def _hour_range(day):
    start_midnight = _truncate_datetime(day)
    hour = start_midnight
    while hour < start_midnight + timedelta(days=1):
        yield hour
        hour = hour + timedelta(hours=1)

def sun_calendar(city_name, start, end):
    """
    Returns an hourly sun calendar for the given city. The calendar contains the
    information whether or not the sun is up during a given day and hour.
    """

    records = []
    d = start
    while d < end:
        records += [[t] for t in _hour_range(d)]
        d = d + timedelta(days=1)

    return pd.DataFrame.from_records(records, columns=['timestamp'])
