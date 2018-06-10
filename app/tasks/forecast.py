from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast


def check_forecast_preconditions():
    """
    Depending on the model used, we rely on some historical data
    when the generation forecast is done, as well as weather forecasts
    for some time into the future. This task checks if we have up-to-date
    data in the database.
    """

    hour_now = datetime.now().replace(minute=0, second=0, microsecond=0)
    num_hours = 48
    weather_forecast_hours = 6

    generation_reports = GenerationReport.query.filter(
        GenerationReport.timestamp >= hour_now - timedelta(hours=num_hours)
    ).all()

    weather_forecasts = WeatherForecast.query.filter(
        WeatherForecast.timestamp >= hour_now - timedelta(hours=num_hours)
    ).all()

    return (
        len(generation_reports) >= num_hours
        and len(weather_forecasts) >= num_hours + weather_forecast_hours
    )
