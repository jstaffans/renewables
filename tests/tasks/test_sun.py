import pytest
import pandas as pd
from datetime import datetime, timedelta

from app.tasks import sun


class TestSun(object):
    def test_24_hours(self):
        start = datetime(2018, 4, 25, 21, 53, 0)
        end = start + timedelta(days=1)
        calendar = sun.sun_calendar("Berlin", start, end)

        rows, _ = calendar.shape
        assert rows == 24
        assert calendar.iloc[0].name == datetime(2018, 4, 25)
        assert calendar.iloc[23].name == datetime(2018, 4, 25, 23)

    def test_48_hours(self):
        start = datetime(2018, 4, 25, 21, 53, 0)
        end = start + timedelta(days=2)
        calendar = sun.sun_calendar("Berlin", start, end)

        rows, _ = calendar.shape
        assert rows == 48
        assert calendar.iloc[0].name == datetime(2018, 4, 25)
        assert calendar.iloc[47].name == datetime(2018, 4, 26, 23)

    def test_day_and_night(self):
        start = datetime(2018, 4, 25, 21, 53, 0)
        calendar = sun.sun_calendar("Berlin", start, start + timedelta(days=1))
        assert calendar.iloc[0]["sun"] == 0
        assert calendar.iloc[11]["sun"] > 0.999
