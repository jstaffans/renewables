import pandas as pd
import pytz
from datetime import timedelta
from astral import Astral
from app.util import hour_range
from scipy.signal import savgol_filter


def _is_sun_up(sunrise, sunset, t_utc):
    return 1 if sunrise < t_utc < sunset else 0


def sun_calendar(city_name, start, end):
    """
    Returns an hourly sun calendar for the given city. The calendar contains the
    information whether or not the sun is up during a given day and hour.
    The range is start to end, whole hours, exclusive.

    Timestamps are in UTC. Start and end dates are interpreted as UTC.
    """
    start_utc = pytz.utc.localize(start)
    end_utc = pytz.utc.localize(end)
    end_utc_inclusive = end_utc + timedelta(days=1)
    a = Astral()
    city = a[city_name]
    d = start_utc
    records = []
    while d < end_utc_inclusive:
        sunrise = city.sunrise(date=d)
        sunset = city.sunset(date=d)
        records += [
            [t.replace(tzinfo=None), _is_sun_up(sunrise, sunset, t)]
            for t in hour_range(d)
        ]
        d = d + timedelta(days=1)

    # smooth out transition between night and day to give model a chance to react
    smoothed = savgol_filter([r[1] for r in records], 5, 1)
    for i, r in enumerate(records):
        records[i][1] = smoothed[i] if smoothed[i] >= 0 else 0

    calendar = pd.DataFrame.from_records(
        records, columns=["timestamp", "sun"]
    ).set_index("timestamp")

    # return just the start-end window we want
    return calendar.ix[start : end - timedelta(hours=1)]


def sun_calendar_hours_past(city_name, hour, hours_past):
    start = hour - timedelta(hours=hours_past)
    end = hour
    return sun_calendar(city_name, start, end)
