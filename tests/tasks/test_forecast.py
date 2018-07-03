import pytest
from datetime import datetime, timedelta
from flask.ext.testing import TestCase
import pandas as pd

from app import create_app, db
from app.model import (
    ModelParameters,
    GenerationReport,
    WeatherForecast,
    historical_data as db_historical_data,
)
from app.tasks.forecast import prepare_forecast
from app.util import hour_now
from tests.df_helper import (
    timestamped_single_generation_report,
    timestamped_single_weather_forecast,
    weather_report_range,
    generation_report_range,
)
from tests.model_helper import no_historical_data


class TestForecast(TestCase):

    model_params = ModelParameters(hours_past=25, hours_forecast=6)

    def create_app(self):
        return create_app("app.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def stub_generation_task(self, start, end):
        return generation_report_range(start, end)

    def stub_weather_task(self, start, end):
        return weather_report_range(start, end)

    def test_forecast_preparation(self):
        assert len(GenerationReport.query.all()) == 0
        assert len(WeatherForecast.query.all()) == 0

        hour = hour_now()

        prepare_forecast(
            no_historical_data,
            self.stub_generation_task,
            self.stub_weather_task,
            self.model_params,
            hour,
        )

        generation_reports = GenerationReport.query.order_by(
            GenerationReport.timestamp
        ).all()
        weather_reports_and_forecasts = WeatherForecast.query.order_by(
            WeatherForecast.timestamp
        ).all()

        assert len(generation_reports) == 26

        if hour.minute == 0 and hour.second == 0 and hour.microsecond == 0:
            assert (
                len(weather_reports_and_forecasts)
                == self.model_params.hours_past + self.model_params.hours_forecast
            )
        else:
            assert (
                len(weather_reports_and_forecasts)
                == self.model_params.hours_past + self.model_params.hours_forecast + 1
            )

        # running preparation task again should not update any data
        generation_reports_copy = generation_reports.copy()
        weather_reports_copy = weather_reports_and_forecasts.copy()

        prepare_forecast(
            db_historical_data,
            self.stub_generation_task,
            self.stub_weather_task,
            self.model_params,
            hour,
        )

        generation_reports = GenerationReport.query.order_by(
            GenerationReport.timestamp
        ).all()
        weather_reports_and_forecasts = WeatherForecast.query.order_by(
            WeatherForecast.timestamp
        ).all()

        assert generation_reports_copy == generation_reports
        assert weather_reports_copy == weather_reports_and_forecasts

    def test_weather_forecasts_are_shifted_by_one_hour(self):
        historical_weather_range_datetimes = []

        hour = hour_now()

        def stub_weather_task(start, end):
            if start < hour:
                historical_weather_range_datetimes.append(start)
                historical_weather_range_datetimes.append(end)
            return weather_report_range(start, end)

        prepare_forecast(
            no_historical_data,
            self.stub_generation_task,
            stub_weather_task,
            self.model_params,
            hour,
        )

        weather_reports_and_forecasts = WeatherForecast.query.order_by(
            WeatherForecast.timestamp
        ).all()

        # Rely on LRU cache of weather_report_range
        raw_weather_data = weather_report_range(*historical_weather_range_datetimes)
        assert (
            weather_reports_and_forecasts[0].temperature
            == raw_weather_data.ix[1, "temperature"]
        )
