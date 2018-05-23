from datetime import timedelta

def _truncate_datetime(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def hour_range(day):
    start_midnight = _truncate_datetime(day)
    hour = start_midnight
    while hour < start_midnight + timedelta(days=1):
        yield hour
        hour = hour + timedelta(hours=1)
