import os
import json
import pytest
import mock
import pandas as pd
import numpy.testing as npt
from datetime import datetime, timedelta
from functools import partial

from app.tasks.weather import weather as weather_task


def weather_response(api_token, lat, lon, date):
    with open(
        os.path.join(os.path.dirname(__file__), "weather_2017-06-01.json"), "r"
    ) as f:
        r = json.load(f)
    return r


class TestWeather(object):
    weather_for = partial(weather_task, "test_token", "Berlin")

    @mock.patch("app.tasks.weather._raw_weather", side_effect=weather_response)
    def test_single_day_weather(self, weather_response_function):
        data = self.weather_for(datetime(2017, 6, 1), datetime(2017, 6, 2))
        rows, _ = data.shape
        assert rows == 24

    @mock.patch("app.tasks.weather._raw_weather", side_effect=weather_response)
    def test_multiple_day_weather(self, weather_response_function):
        data = self.weather_for(datetime(2017, 6, 1, 12), datetime(2017, 6, 2, 12))
        rows, _ = data.shape
        assert rows == 48

    @mock.patch("app.tasks.weather._raw_weather", side_effect=weather_response)
    def test_weather_fill_forward_missing_data(self, weather_response_function):
        # Cloud cover is a None value except the first reading - should be filled
        data = self.weather_for(datetime(2017, 6, 1), datetime(2017, 6, 2))
        expected_cloud_cover = [0.88] * 24
        npt.assert_array_equal(data["cloud_cover"].values, expected_cloud_cover)
