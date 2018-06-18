from functools import lru_cache
from pyiso import client_factory
from datetime import datetime, timedelta
from funcy import compose, identity, retry
from itertools import repeat
from urllib.error import HTTPError
import pandas as pd
import numpy as np

from app.model import RENEWABLES, NON_RENEWABLES
from app.util import full_hour_series


@retry(5, errors=HTTPError)
@lru_cache()
def raw_generation(ba_name, control_area, start, end):
    entso = client_factory(ba_name)
    data = entso.get_generation(
        latest=True, control_area=control_area, start_at=start, end_at=end
    )
    return pd.DataFrame(data)


def deduplicate(raw):
    """Sum generation readings that have the same fuel_name"""
    by_fuel = raw.groupby(["fuel_name", "timestamp", "freq"])
    return by_fuel.agg({"gen_MW": np.sum}).reset_index()


def add_missing_megawatts(raw):
    """Add 0 generation reading for missing timestamps"""
    by_fuel = raw.groupby(["fuel_name"])
    return pd.concat(
        [_group_without_missing_data(g) for _, g in by_fuel], ignore_index=True
    )


def _group_without_missing_data(group):
    source = group.iloc[0]
    source_zero_mw = pd.DataFrame([source])
    source_zero_mw.at[source_zero_mw.index[0], "gen_MW"] = 0
    # in case first 15 minutes are missing: make sure series starts at 15 minutes past
    start = source["timestamp"].replace(minute=15)
    end = group.iloc[-1].timestamp
    series = full_hour_series(start, end, "15min")

    def filler(t):
        filler = source_zero_mw.copy()
        filler.at[filler.index[0], "timestamp"] = t
        return filler

    def df_for_timestamp(t):
        df = group[group["timestamp"] == t]
        return df if len(df) > 0 else filler(t)

    return pd.concat([df_for_timestamp(t) for t in series], ignore_index=True)


def downsample(raw):
    """Downsample to 1 hour (original reports use 15m interval)."""
    assert raw[raw["freq"] != "15m"].empty

    # The last generation report of the day has a timestamp that is
    # day+1 at 00:00 (each report contains data of the previous 15 minutes).
    # Adjust timestamp a little to get all generation reports within the
    # boundary of one day.
    raw["timestamp_adjusted"] = raw["timestamp"] - pd.Timedelta("1s")

    raw["date"] = raw["timestamp_adjusted"].dt.date
    raw["hour"] = raw["timestamp_adjusted"].dt.hour

    data = (
        raw.groupby([lambda i: i // 4, "fuel_name", "date", "hour"])
        .agg({"gen_MW": np.mean})
        .reset_index()
        .drop(["level_0"], axis=1)
    )

    timestamps = data.apply(
        lambda x: pd.to_datetime(x["hour"], unit="h", origin=x["date"]), axis=1
    )

    return data.assign(timestamp=timestamps).drop(["date", "hour"], axis=1)


def pivot(df):
    """Produce a tidy data set by pivoting each fuel_name into its own column."""
    return df.pivot(index="timestamp", columns="fuel_name")


def flatten(df):
    return df["gen_MW"]


def normalise_fuels(df):
    """Restrict fuels to list of known fuels (add zero gen_MW if missing)."""
    rows, _ = df.shape
    zero = list(repeat(0, rows))

    def zero_df(fuels):
        d = {fuel: zero for fuel in fuels}
        d["timestamp"] = df.index
        return pd.DataFrame(d).set_index("timestamp")

    renewables = zero_df(RENEWABLES)
    non_renewables = zero_df(NON_RENEWABLES)

    valid_columns = set(renewables.columns.tolist() + non_renewables.columns.tolist())
    df_columns = set(df.columns.tolist())
    normalised = df.drop(df_columns - valid_columns, axis=1, errors="ignore")
    return normalised.combine_first(renewables).combine_first(non_renewables)


def ratio(df):
    """
    Sum together renewable and non-renewable fuel types.
    This is somewhat redundant since the individual fuel types are also returned.
    """
    new = df.copy()

    new["renewables"] = sum([new[fuel_type] for fuel_type in RENEWABLES])
    new["non_renewables"] = new.sum(axis=1) - 2 * new["renewables"]
    return new


def round(df):
    """Let's only work with whole numbers (MW)."""
    return df.apply(np.round)


transform = compose(
    round,
    ratio,
    normalise_fuels,
    flatten,
    pivot,
    downsample,
    add_missing_megawatts,
    deduplicate,
)


def generation(ba_name, control_area, start, end):
    """
    Returns a per-hour generation report as a Pandas DataFrame.
    Start and end should be in UTC, since the ENTSO-E API interprets
    datetimes as being in UTC. The timestamps in the returned
    report are also UTC.
    """
    raw = raw_generation(ba_name, control_area, start, end)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"])
    return transform(raw)
