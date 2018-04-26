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

def _is_sun_up(sunrise, sunset, t):
    t_with_tz = t.replace(tzinfo=sunrise.tzinfo)
    return 1 if sunrise < t_with_tz < sunset else 0

def sun_calendar(city_name, start, end):
    """
    Returns an hourly sun calendar for the given city. The calendar contains the
    information whether or not the sun is up during a given day and hour.
    """

    a = Astral()
    city = a[city_name]
    # d = start.replace(tzinfo=city.tz)
    d = start
    records = []
    while d < end:
        sunrise = city.sunrise(date=d)
        sunset = city.sunset(date=d)
        records += [[t, _is_sun_up(sunrise, sunset, t)] for t in _hour_range(d)]
        d = d + timedelta(days=1)

    return pd.DataFrame.from_records(records, columns=['timestamp', 'sun']).set_index('timestamp')
