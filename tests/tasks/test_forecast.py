import pytest
from datetime import datetime, timedelta
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport, WeatherForecast
from app.tasks.forecast import (
    check_historical_data_present,
)
from app.util import hour_now
from tests.df_helper import (
    timestamped_single_generation_report,
    timestamped_single_weather_forecast,
)


class TestForecast(TestCase):
    def create_app(self):
        return create_app("app.TestingConfig")

    def test_historical_data_missing(self):
        hour = hour_now()

        report = timestamped_single_generation_report(hour)
        GenerationReport.insert("EU", "TEST_CA", report)

        weather_forecast = timestamped_single_weather_forecast(hour)
        WeatherForecast.insert("Berlin", weather_forecast)

        assert check_historical_data_present(hour) == False

    def test_historical_data_present(self):
        hour = hour_now()
        h = hour - timedelta(hours=48)

        while h <= hour:
            report = timestamped_single_generation_report(h)
            weather_forecast = timestamped_single_weather_forecast(h)
            GenerationReport.insert("EU", "TEST_CA", report)
            WeatherForecast.insert("Berlin", weather_forecast)
            h = h + timedelta(hours=1)

        assert check_historical_data_present(hour) == True

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
