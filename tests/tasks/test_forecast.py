import pytest
from datetime import datetime, timedelta
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import (
    GenerationReport,
    WeatherForecast,
    historical_data as db_historical_data,
)
from app.tasks.forecast import (
    prepare_forecast,
    HOURS_PAST,
    WEATHER_FORECAST_HOURS_FUTURE,
)
from app.util import hour_now
from tests.df_helper import (
    timestamped_single_generation_report,
    timestamped_single_weather_forecast,
    weather_report_range,
    generation_report_range,
)
from tests.model_helper import no_historical_data


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
            return weather_report_range(start, end)

        assert len(GenerationReport.query.all()) == 0
        assert len(WeatherForecast.query.all()) == 0

        hour = hour_now()

        prepare_forecast(
            no_historical_data, stub_generation_task, stub_weather_task, hour
        )

        generation_reports = GenerationReport.query.order_by(
            GenerationReport.timestamp
        ).all()
        weather_reports_and_forecasts = WeatherForecast.query.order_by(
            WeatherForecast.timestamp
        ).all()

        assert len(generation_reports) >= HOURS_PAST

        # ENTSO API returns full days only, so the report for the first day starts at midnight,
        # and the last day ends  at 23:00
        assert generation_reports[0].timestamp.hour == 0
        assert generation_reports[-1].timestamp.hour == 23

        assert len(weather_reports_and_forecasts) in [
            HOURS_PAST + WEATHER_FORECAST_HOURS_FUTURE,
            HOURS_PAST + WEATHER_FORECAST_HOURS_FUTURE + 1,
        ]

        # running preparation task again should not update any data
        generation_reports_copy = generation_reports.copy()
        weather_reports_copy = weather_reports_and_forecasts.copy()

        prepare_forecast(
            db_historical_data, stub_generation_task, stub_weather_task, hour
        )

        generation_reports = GenerationReport.query.order_by(
            GenerationReport.timestamp
        ).all()
        weather_reports_and_forecasts = WeatherForecast.query.order_by(
            WeatherForecast.timestamp
        ).all()

        assert generation_reports_copy == generation_reports
        assert weather_reports_copy == weather_reports_and_forecasts
