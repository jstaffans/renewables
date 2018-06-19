import pytest
from datetime import datetime, timedelta
import pytz


class TestUtil(object):
    def test_tz_comparison(self):
        # can you compare datetimes with different timezones?
        berlin = pytz.timezone('Europe/Berlin')
        berlin_dt = berlin.localize(datetime(2018, 6, 19, 12))
        utc_dt = pytz.utc.localize(datetime(2018, 6, 19, 10))
        assert berlin_dt == utc_dt
