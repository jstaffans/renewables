import pytest
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import GenerationReport
from tests.df_helper import single_generation_report


class TestModel(TestCase):
    def create_app(self):
        return create_app("app.TestingConfig")

    def test_report_insertion(self):
        report = single_generation_report()
        GenerationReport.insert("EU", "TEST_CA", report)
        db_reports = GenerationReport.query.all()
        assert len(db_reports) == 1
        assert db_reports[0].renewables == 12266.0
        assert db_reports[0].non_renewables == 4470.0

    def test_weather_forecast_insertion(self):
        report = single_weather_forecast()
        GenerationReport.insert("EU", "TEST_CA", report)
        db_reports = GenerationReport.query.all()
        assert len(db_reports) == 1
        assert db_reports[0].renewables == 12266.0
        assert db_reports[0].non_renewables == 4470.0

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
