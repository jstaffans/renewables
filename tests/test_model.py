import pytest
import pandas as pd
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import (
    GenerationReport,
    WeatherForecast,
    is_historical_data_present,
    prediction_window,
)
from app.util import hour_now
from tests.df_helper import single_generation_report, single_weather_forecast
from tests.model_helper import full_historical_data, partial_historical_data


class TestModel(TestCase):
    def create_app(self):
        return create_app("app.TestingConfig")

    def test_report_insertion(self):
        report = single_generation_report()
        GenerationReport.insert_or_replace(report)
        db_reports = GenerationReport.query.all()
        assert len(db_reports) == 1

    def test_weather_forecast_insertion(self):
        forecast = single_weather_forecast()
        WeatherForecast.insert_or_replace(forecast)
        db_forecasts = WeatherForecast.query.all()
        assert len(db_forecasts) == 1

    def test_replacement(self):
        forecast = single_weather_forecast()
        WeatherForecast.insert_or_replace(forecast)
        forecast.temperature = 1000.0
        WeatherForecast.insert_or_replace(forecast)
        db_forecasts = WeatherForecast.query.all()
        assert len(db_forecasts) == 1
        assert db_forecasts[0].temperature == 1000.0

    def test_historical_data_missing(self):
        generation_reports, weather_forecasts = partial_historical_data(hour_now(), 48)
        assert (
            is_historical_data_present(generation_reports, weather_forecasts, 48)
            == False
        )

    def test_historical_data_present(self):
        generation_reports, weather_forecasts = full_historical_data(hour_now(), 48)
        assert (
            is_historical_data_present(generation_reports, weather_forecasts, 48)
            == True
        )

    def test_prediction_window_fully_backed_by_historical_data(self):
        hour = hour_now()
        generation_reports, weather_forecasts = full_historical_data(hour, 48)
        db.session.add_all(generation_reports)
        db.session.add_all(weather_forecasts)
        db.session.commit()

        hours_past = 25
        window = prediction_window(hour, hours_past)

        assert isinstance(window, pd.DataFrame)

        expected_columns = [
            "renewables",
            "non_renewables",
            "sun",
            "wind_speed",
            "cloud_cover",
            "temperature",
            "pressure",
        ]
        rows, _ = window.shape
        assert rows == hours_past
        assert set(expected_columns) == set(window.columns.values)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
