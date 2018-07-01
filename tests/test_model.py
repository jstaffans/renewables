import pytest
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport, WeatherForecast, is_historical_data_present
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

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
