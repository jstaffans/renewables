import pandas as pd
import numpy as np
import pytz
import requests
from tzlocal import get_localzone
from astral import Astral
from datetime import datetime, timedelta
from funcy import retry
from urllib.error import HTTPError
from app.util import hour_range


LOCAL_ZONE = get_localzone()


@retry(5, errors=HTTPError)
def _raw_weather(api_token, lat, lon, date):
    d = date.replace(microsecond=0).isoformat()
    r = requests.get(
        f"https://api.darksky.net/forecast/{api_token}/{lat},{lon},{d}Z?units=si"
    )
    return r.json()


def _as_dataframe(data, date):
    def to_utc(dt):
        # Dark Sky API always returns local timestamps, but we need UTC.
        # is_dst is usually ignored and only used during DST transition time.
        local_dt = LOCAL_ZONE.localize(dt, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    timestamps = list(hour_range(date))
    utc_timestamps = [to_utc(dt) for dt in timestamps]
    hourly = data["hourly"]["data"]
    keys = ["cloudCover", "temperature", "windSpeed", "pressure"]
    weather = [[d.get(k) for k in keys] for d in hourly]
    df1 = pd.DataFrame(utc_timestamps, columns=["timestamp"])
    df2 = pd.DataFrame(
        weather, columns=["cloud_cover", "temperature", "wind_speed", "pressure"]
    )
    return pd.concat([df1, df2], axis=1).set_index("timestamp")


def _tidy(df):
    return df.fillna(value=np.NaN).fillna(method="ffill")


def _num_days(start, end):
    if start.hour == end.hour == 0:
        return (end - start).days
    else:
        return (end.replace(hour=12) - start.replace(hour=12)).days + 1


def weather(api_token, city, start, end):
    """
    Returns an hourly report of cloud cover, wind and temperature data for the
    given city. The report is always in full days. Timestamps are in UTC.
    """
    a = Astral()
    city = a[city]

    # hour=0 would give us the previous day. Dark Sky always returns full days so
    # we can just make one request per day from start to end, always at midday.
    d = start.replace(hour=12)

    dfs = []

    for i in range(_num_days(start, end)):
        weather = _raw_weather(api_token, city.latitude, city.longitude, d)
        df = _as_dataframe(weather, d)
        dfs.append(df)
        d = d + timedelta(days=1)

    return _tidy(pd.concat(dfs))
