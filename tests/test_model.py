import pytest
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport, WeatherForecast
from tests.df_helper import single_generation_report, single_weather_forecast


class TestModel(TestCase):
    def create_app(self):
        return create_app("app.TestingConfig")

    def test_report_insertion(self):
        report = single_generation_report()
        GenerationReport.insert("EU", "TEST_CA", report)
        db_reports = GenerationReport.query.all()
        assert len(db_reports) == 1

    def test_weather_forecast_insertion(self):
        forecast = single_weather_forecast()
        WeatherForecast.insert("Berlin", forecast)
        db_forecasts = WeatherForecast.query.all()
        assert len(db_forecasts) == 1

    def test_replacement(self):
        forecast = single_weather_forecast()
        WeatherForecast.insert("Berlin", forecast)
        WeatherForecast.insert("Berlin", forecast)
        db_forecasts = WeatherForecast.query.all()
        assert len(db_forecasts) == 1

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
