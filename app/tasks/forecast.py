from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast


HOURS_PAST = 48
WEATHER_FORECAST_HOURS_FUTURE = 6


def check_historical_data_present(hour):
    """
    Depending on the model used, we rely on some historical data
    when the generation forecast is done. This task checks that we
    have the necessary data in the database.
    """

    generation_reports = GenerationReport.query.filter(
        GenerationReport.timestamp >= hour - timedelta(hours=HOURS_PAST)
    ).all()

    weather_forecasts = WeatherForecast.query.filter(
        WeatherForecast.timestamp >= hour - timedelta(hours=HOURS_PAST)
    ).all()

    return (
        len(generation_reports) >= HOURS_PAST and len(weather_forecasts) >= HOURS_PAST
    )


def prepare_forecast(weather_task, api_token, city_name, hour):
    """
    Prepare database for calculating a forecast.
    """
    forecast_horizon = hour + timedelta(hours=WEATHER_FORECAST_HOURS_FUTURE)

    weather_forecast = weather_task(api_token, city_name, hour, forecast_horizon)
    weather_forecast_window = weather_forecast.ix[hour:forecast_horizon]

    WeatherForecast.insert(city_name, weather_forecast_window)
