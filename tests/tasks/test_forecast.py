import pytest
from datetime import datetime, timedelta
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport, WeatherForecast
from app.tasks.forecast import prepare_forecast, WEATHER_FORECAST_HOURS_FUTURE
from app.util import hour_now
from tests.df_helper import (
    timestamped_single_generation_report,
    timestamped_single_weather_forecast,
    current_weather_forecast,
    generation_report_range,
)
from tests.model_helper import full_historical_data, partial_historical_data


class TestForecast(TestCase):
    def create_app(self):
        return create_app("app.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_forecast_preparation(self):
        def stub_generation_task(start, end):
            return generation_report_range(start, end)

        def stub_weather_task(start, end):
            return current_weather_forecast()

        assert len(WeatherForecast.query.all()) == 0

        hour = hour_now()

        prepare_forecast(
            partial_historical_data, stub_generation_task, stub_weather_task, hour
        )

        forecasts = WeatherForecast.query.all()

        for i in range(WEATHER_FORECAST_HOURS_FUTURE):
            assert forecasts[i].timestamp == hour + timedelta(hours=i)

        assert len(forecasts) in [
            WEATHER_FORECAST_HOURS_FUTURE,
            WEATHER_FORECAST_HOURS_FUTURE + 1,
        ]
