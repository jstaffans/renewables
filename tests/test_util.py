import pytest
import pandas as pd
from app.util import full_hour_series


class TestUtil(object):
    def test_two_hour_series(self):
        start = pd.Timestamp(2018, 1, 1, 0)
        end = pd.Timestamp(2018, 1, 1, 2)
        series = full_hour_series(start, end, "15min")
        assert len(series) == 8

    def test_min_one_hour_series(self):
        start = pd.Timestamp(2018, 1, 1, 0)
        end = pd.Timestamp(2018, 1, 1, 0, 1)
        series = full_hour_series(start, end, "15min")
        assert len(series) == 4

    def test_zero_hour_series(self):
        start = pd.Timestamp(2018, 1, 1, 0)
        end = pd.Timestamp(2018, 1, 1, 0, 0)
        series = full_hour_series(start, end, "15min", min_hours=0)
        assert len(series) == 0

    def test_24_hour_series(self):
        start = pd.Timestamp(2018, 1, 1, 0)
        end = pd.Timestamp(2018, 1, 2, 0)
        series = full_hour_series(start, end, "15min")
        assert len(series) == 24 * 4

    def test_period_count_starts_at_full_hour(self):
        # a start offset of 15 minutes is ignored when number of periods is calculated
        start = pd.Timestamp(2018, 1, 1, 0, 15)
        end = pd.Timestamp(2018, 1, 2, 0)
        series = full_hour_series(start, end, "15min")
        assert len(series) == 24 * 4
        assert series[0] == start
        assert series[-1] == end
