import pytest
from datetime import datetime, timedelta
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport, WeatherForecast, ForecastTimeAndLocation
from app.tasks.forecast import (
    check_historical_data_present,
    prepare_forecast,
    WEATHER_FORECAST_HOURS_FUTURE,
)
from app.util import hour_now
from tests.df_helper import (
    timestamped_single_generation_report,
    timestamped_single_weather_forecast,
    current_weather_forecast,
)


class TestForecast(TestCase):

    time_and_location = ForecastTimeAndLocation(ba_name="EU", control_area="TEST_CA", city="Berlin", hour=hour_now())

    def create_app(self):
        return create_app("app.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_historical_data_missing(self):
        report = timestamped_single_generation_report(self.time_and_location.hour)
        GenerationReport.insert_or_replace("EU", "TEST_CA", report)

        weather_forecast = timestamped_single_weather_forecast(self.time_and_location.hour)
        WeatherForecast.insert_or_replace("Berlin", weather_forecast)

        assert check_historical_data_present(self.time_and_location.hour) == False

    def test_historical_data_present(self):
        h = self.time_and_location.hour - timedelta(hours=48)

        while h <= self.time_and_location.hour:
            report = timestamped_single_generation_report(h)
            weather_forecast = timestamped_single_weather_forecast(h)
            GenerationReport.insert_or_replace("EU", "TEST_CA", report)
            WeatherForecast.insert_or_replace("Berlin", weather_forecast)
            h = h + timedelta(hours=1)

        assert check_historical_data_present(self.time_and_location.hour) == True

    def test_forecast_preparation(self):
        def stub_weather_task(api_token, city_name, start, end):
            return current_weather_forecast()

        assert len(WeatherForecast.query.all()) == 0

        prepare_forecast(stub_weather_task, "test_token", self.time_and_location)

        forecasts = WeatherForecast.query.all()

        for i in range(WEATHER_FORECAST_HOURS_FUTURE):
            assert forecasts[i].timestamp == self.time_and_location.hour + timedelta(hours=i)

        assert len(forecasts) in [
            WEATHER_FORECAST_HOURS_FUTURE,
            WEATHER_FORECAST_HOURS_FUTURE + 1,
        ]

