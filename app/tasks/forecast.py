from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import WeatherForecast


def check_historical_data_present():
    """
    Depending on the model used, we rely on some historical data
    when the generation forecast is done. This task checks if
    we have up-to-date data in the database.
    """
    weather_forecast_reports = WeatherForecast.query.filter(WeatherForecast.timestamp >= datetime.now() - timedelta(days=2)).all()

    # TODO

    return weather_forecast_reports
