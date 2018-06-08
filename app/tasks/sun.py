import pandas as pd
import pytz
from datetime import timedelta
from astral import Astral
from app.util import hour_range
from scipy.signal import savgol_filter

def _is_sun_up(sunrise, sunset, t):
    t_utc = pytz.timezone('UTC').localize(t)
    return 1 if sunrise < t_utc < sunset else 0

def sun_calendar(city_name, start, end):
    """
    Returns an hourly sun calendar for the given city. The calendar contains the
    information whether or not the sun is up during a given day and hour.

    Timestamps are in UTC.
    """
    a = Astral()
    city = a[city_name]
    d = start
    records = []
    while d < end:
        sunrise = city.sunrise(date=d)
        sunset = city.sunset(date=d)
        records += [[t, _is_sun_up(sunrise, sunset, t)] for t in hour_range(d)]
        d = d + timedelta(days=1)

    # smooth out transition between night and day to give model a chance to react
    smoothed = savgol_filter([r[1] for r in records], 5, 1)
    for i, r in enumerate(records):
        records[i][1] = smoothed[i] if smoothed[i] >= 0 else 0

    return pd.DataFrame.from_records(records, columns=['timestamp', 'sun']).set_index('timestamp')
