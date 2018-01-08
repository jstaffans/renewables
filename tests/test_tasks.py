import os
import pytest
import pandas as pd
from dateutil.parser import parse
from app import tasks

@pytest.fixture(scope='module')
def simple():
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'generation_2018-01-02_small.csv'),
                       parse_dates=True)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data


class TestGeneration(object):

    def test_null_replacement(self):
        data = simple()
        without_nulls = tasks.add_missing(data)
        rows, _ = without_nulls.shape
        assert rows == 192
        assert without_nulls.iloc[0]['gen_MW'] > 0
        assert without_nulls.iloc[0]['timestamp'] == parse('2018-01-02 00:15:00')
        assert without_nulls.iloc[1]['gen_MW'] == 0
        assert without_nulls.iloc[1]['timestamp'] == parse('2018-01-02 00:30:00')
        assert without_nulls.iloc[191]['gen_MW'] == 0
        assert without_nulls.iloc[191]['timestamp'] == parse('2018-01-03 00:00:00')



