import os
import pytest
import pandas as pd
from flask.ext.testing import TestCase

from app import create_app, db
from app.model import csv_to_pd, insert_generation_report, GenerationReport

def _csv(filename):
   return os.path.join(os.path.dirname(__file__), filename)

@pytest.fixture(scope='module')
def single_reading():
    return csv_to_pd(_csv('generation_2018_single.csv'))

class TestModel(TestCase):

    settings_override = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///../test_renewables.db',
        'TESTING': True,
    }

    def create_app(self):
        return create_app(self.settings_override)

    def test_report_insertion(self):
        report = single_reading()
        insert_generation_report('EU', 'TEST_CA', report)
        db_reports = GenerationReport.query.all()
        assert len(db_reports) == 1
        assert db_reports[0].renewables == 12266.0
        assert db_reports[0].non_renewables == 4470.0

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

