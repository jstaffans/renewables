import os
import pytest
import pandas as pd
from dateutil.parser import parse
from app.tasks import generation

def _read_csv(filename):
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), filename),
                       parse_dates=True)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data

@pytest.fixture(scope='module')
def dedup():
    return _read_csv('generation_2018-01-02_dedup.csv')

@pytest.fixture(scope='module')
def simple():
    return _read_csv('generation_2018-01-02_small.csv')

@pytest.fixture(scope='module')
def full():
    return _read_csv('generation_2018-01-02_orig.csv')

class TestGeneration(object):

    def test_deduplication(self):
        data = dedup()
        deduplicated = generation.deduplicate(data)
        rows, _ = deduplicated.shape
        assert rows == 2
        assert deduplicated[deduplicated['fuel_name'] == 'coal'].iloc[0]['gen_MW'] == 400

    def test_null_replacement(self):
        data = simple()
        without_nulls = generation.add_missing_megawatts(data)
        rows, _ = without_nulls.shape
        assert rows == 192
        assert without_nulls.iloc[0]['gen_MW'] > 0
        assert without_nulls.iloc[0]['timestamp'] == parse('2018-01-02 00:15:00')
        assert without_nulls.iloc[1]['gen_MW'] == 0
        assert without_nulls.iloc[1]['timestamp'] == parse('2018-01-02 00:30:00')
        assert without_nulls.iloc[191]['gen_MW'] == 0
        assert without_nulls.iloc[191]['timestamp'] == parse('2018-01-03 00:00:00')

    def test_downsampling(self):
        data = simple()
        transformed = generation.downsample(data)
        rows, _ = transformed.shape
        assert transformed[transformed['fuel_name'] == 'wind'].iloc[0]['gen_MW'] == 25

    def test_full_series(self):
        data = full()
        transformed = generation.transform(data)
        assert transformed.iloc[24]['fuel_name'] != transformed.iloc[23]['fuel_name']
        assert transformed.iloc[48]['fuel_name'] != transformed.iloc[47]['fuel_name']
