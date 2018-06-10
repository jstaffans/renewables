import pytest
from datetime import datetime, timedelta
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport, WeatherForecast
from app.tasks.forecast import check_historical_data_present
from tests.df_helper import (
    timestamped_single_generation_report,
    timestamped_single_weather_forecast,
)


class TestForecast(TestCase):
    def create_app(self):
        return create_app("app.TestingConfig")

    def test_historical_data_missing(self):
        hour_now = datetime.now().replace(minute=0, second=0, microsecond=0)

        report = timestamped_single_generation_report(hour_now)
        GenerationReport.insert("EU", "TEST_CA", report)

        weather_forecast = timestamped_single_weather_forecast(hour_now)
        WeatherForecast.insert("Berlin", weather_forecast)

        assert check_historical_data_present() == False

    def test_historical_data_present(self):
        hour_now = datetime.now().replace(minute=0, second=0, microsecond=0)
        h = hour_now - timedelta(hours=48)

        while h <= hour_now:
            report = timestamped_single_generation_report(h)
            weather_forecast = timestamped_single_weather_forecast(h)
            GenerationReport.insert("EU", "TEST_CA", report)
            WeatherForecast.insert("Berlin", weather_forecast)
            h = h + timedelta(hours=1)

        assert check_historical_data_present() == True

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
