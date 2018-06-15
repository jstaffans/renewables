from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast


# How many hours of data is needed depends on the forecast model used.
# 48 hours is a conservative number that should be enough even if the
# model changes.

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


def update_weather_forecast(weather_task, api_token, time_and_location):
    """
    Fetches latest weather forecast and saves it to the database.
    """
    forecast_horizon = time_and_location.hour + timedelta(hours=WEATHER_FORECAST_HOURS_FUTURE)
    weather_forecast = weather_task(
        api_token, time_and_location.city, time_and_location.hour, forecast_horizon
    )
    weather_forecast_window = weather_forecast.ix[time_and_location.hour:forecast_horizon]
    WeatherForecast.insert_or_replace(time_and_location.city, weather_forecast_window)


def prepare_forecast(weather_task, api_token, time_and_location):
    """
    Prepare database for calculating a forecast.

    - always fetch latest weather forecast
    - maybe fetch historical data if missing
    """

    update_weather_forecast(weather_task, api_token, time_and_location)

    # TODO: historical data
