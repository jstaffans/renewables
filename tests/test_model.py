import pytest
import pandas as pd
from datetime import timedelta
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import (
    GenerationReport,
    GenerationPrediction,
    WeatherForecast,
    is_historical_data_present,
    generation_and_weather_window,
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

    def test_window_fully_backed_by_historical_data(self):
        hour = hour_now()
        self._insert_full_historical_data(hour, 48)

        hours_past = 25
        window = generation_and_weather_window(hour, hours_past)

        self._expect_generation_and_weather_window(window, hours_past)

    def test_window_partially_backed_by_historical_data(self):
        hour = hour_now()
        self._insert_full_historical_data(hour, 48)
        self._insert_generation_prediction(hour - timedelta(hours=1))
        self._delete_generation_reports(hour, 1)

        hours_past = 25
        window = generation_and_weather_window(hour, hours_past)

        self._expect_generation_and_weather_window(window, hours_past)

    def test_missing_data_in_window(self):
        hour = hour_now()
        self._insert_full_historical_data(hour, 48)
        self._delete_generation_reports(hour, 1)

        with pytest.raises(ValueError):
            hours_past = 25
            window = generation_and_weather_window(hour, hours_past)

    def test_empty_db(self):
        hour = hour_now()
        with pytest.raises(ValueError):
            hours_past = 25
            window = generation_and_weather_window(hour, hours_past)

    def _insert_full_historical_data(self, hour, hours):
        generation_reports, weather_forecasts = full_historical_data(hour, 48)
        db.session.add_all(generation_reports)
        db.session.add_all(weather_forecasts)
        db.session.commit()

    def _insert_generation_prediction(self, hour):
        generation_prediction = GenerationPrediction(
            timestamp=hour, renewables_ratio=0.6
        )

        db.session.add(generation_prediction)
        db.session.commit()

    def _delete_generation_reports(self, hour, hours_past):
        GenerationReport.query.filter(
            GenerationReport.timestamp >= hour - timedelta(hours=hours_past)
        ).delete()
        db.session.commit()

    def _expect_generation_and_weather_window(self, window, hours_past):
        assert isinstance(window, pd.DataFrame)

        expected_columns = [
            "renewables_ratio",
            "wind_speed",
            "cloud_cover",
            "temperature",
            "pressure",
        ]
        rows, _ = window.shape
        assert rows == hours_past
        assert set(expected_columns) == set(window.columns.values)

        # ratio should never be negative!
        window_with_positive_ratio = window[window.renewables_ratio > 0]
        assert window_with_positive_ratio.shape[0] == rows

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
