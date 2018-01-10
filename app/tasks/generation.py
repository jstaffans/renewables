from functools import lru_cache
from pyiso import client_factory
from datetime import datetime, timedelta
from funcy import compose, identity, retry
from urllib.error import HTTPError
import pandas as pd
import numpy as np

@retry(3, errors=HTTPError)
@lru_cache()
def raw_generation(ba_name, control_area, start, end):
    entso = client_factory(ba_name)
    data = entso.get_generation(latest=True, control_area=control_area, start_at=start, end_at=end)
    return pd.DataFrame(data)

def add_missing_megawatts(raw):
    """Add 0 gen_MW for missing timestamps"""
    by_fuel = raw.groupby(['fuel_name'])
    return pd.concat([_group_without_missing_data(g) for _, g in by_fuel], ignore_index=True)

def _group_without_missing_data(group):
    source = group.iloc[0]
    source_zero_mw = pd.DataFrame([source])
    source_zero_mw.at[source_zero_mw.index[0], 'gen_MW'] = 0
    start = source['timestamp'].replace(hour=0, minute=15)
    series = pd.date_range(start, periods=24*4, freq='15min')

    def filler(t):
        filler = source_zero_mw.copy()
        filler.at[filler.index[0], 'timestamp'] = t
        return filler

    def df_for_timestamp(t):
        df = group[group['timestamp'] == t]
        return df if len(df) > 0 else filler(t)

    return pd.concat([df_for_timestamp(t) for t in series], ignore_index=True)

def group_by_hour(raw):
    raw['timestamp_adjusted'] = raw['timestamp'] - pd.Timedelta('1s')
    raw['date'] = raw['timestamp_adjusted'].dt.date
    raw['hour'] = raw['timestamp_adjusted'].dt.hour

    aggregation = {
        'gen_MW': np.mean,
    }

    return raw\
        .groupby([lambda i: i // 4, 'fuel_name', 'date', 'hour'])\
        .agg(aggregation)\
        .reset_index()\
        .drop(['level_0'], axis=1)

transform = compose(group_by_hour, add_missing_megawatts)

def generation(ba_name='EU', control_area=None, start=None, end=None):
    raw = raw_generation(ba_name, control_area, start, end)
    raw['timestamp'] = pd.to_datetime(raw['timestamp'])
    return transform(raw)