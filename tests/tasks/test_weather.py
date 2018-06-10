import os
import json
import pytest
import mock
import pandas as pd
import numpy.testing as npt
from datetime import datetime, timedelta

from app.tasks.weather import weather as weather_task


def weather_response(api_token, lat, lon, date):
    with open(
        os.path.join(os.path.dirname(__file__), "weather_2017-06-01.json"), "r"
    ) as f:
        r = json.load(f)
    return r


class TestWeather(object):
    @mock.patch("app.tasks.weather._raw_weather", side_effect=weather_response)
    def test_weather(self, weather_response_function):
        data = weather_task(
            "test_token", "Berlin", datetime(2017, 6, 1), datetime(2017, 6, 2)
        )

        rows, _ = data.shape

        assert rows == 24

        # Cloud cover is a None value except the first reading.
        # Should be filled-forward.
        expected_cloud_cover = [0.88] * 24
        npt.assert_array_equal(data["cloud_cover"].values, expected_cloud_cover)
