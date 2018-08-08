import pytest
import pandas as pd
from datetime import datetime, timedelta

from app.sun import sun_calendar, sun_calendar_hours_past


class TestSun(object):
    def test_24_hours(self):
        start = datetime(2018, 4, 25)
        end = start + timedelta(days=1)
        calendar = sun_calendar("Berlin", start, end)

        rows, _ = calendar.shape
        assert rows == 24
        assert calendar.iloc[0].name == datetime(2018, 4, 25)
        assert calendar.iloc[23].name == datetime(2018, 4, 25, 23)

    def test_24_hours_not_midnight(self):
        start = datetime(2018, 4, 25, 6)
        end = start + timedelta(days=1)
        calendar = sun_calendar("Berlin", start, end)
        assert calendar.iloc[0].name == datetime(2018, 4, 25, 6)
        assert calendar.iloc[23].name == datetime(2018, 4, 26, 5)

    def test_48_hours(self):
        start = datetime(2018, 4, 25)
        end = start + timedelta(days=2)
        calendar = sun_calendar("Berlin", start, end)

        rows, _ = calendar.shape
        assert rows == 48
        assert calendar.iloc[0].name == datetime(2018, 4, 25)
        assert calendar.iloc[47].name == datetime(2018, 4, 26, 23)

    def test_day_and_night(self):
        start = datetime(2018, 4, 25)
        calendar = sun_calendar("Berlin", start, start + timedelta(days=1))
        assert calendar.iloc[0]["sun"] == 0
        assert calendar.iloc[11]["sun"] > 0.999

    def test_hours_past(self):
        hour = datetime(2018, 4, 25, 18)
        hours_past = 25
        calendar = sun_calendar_hours_past("Berlin", hour, hours_past)
        rows, _ = calendar.shape
        assert rows == hours_past
        assert calendar.iloc[-1].name == datetime(2018, 4, 25, 17)
