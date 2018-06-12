from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast


HOURS_PAST = 48
WEATHER_FORECAST_HOURS_FUTURE = 6


def check_forecast_preconditions():
    """
    Depending on the model used, we rely on some historical data
    when the generation forecast is done. This task checks that we
    have the necessary data in the database.
    """

    hour_now = datetime.now().replace(minute=0, second=0, microsecond=0)

    generation_reports = GenerationReport.query.filter(
        GenerationReport.timestamp >= hour_now - timedelta(hours=HOURS_PAST)
    ).all()

    weather_forecasts = WeatherForecast.query.filter(
        WeatherForecast.timestamp >= hour_now - timedelta(hours=HOURS_PAST)
    ).all()

    return (
        len(generation_reports) >= HOURS_PAST and len(weather_forecasts) >= HOURS_PAST
    )
