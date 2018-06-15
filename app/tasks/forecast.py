from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast, is_historical_data_present


# How many hours of data is needed depends on the forecast model used.
# 48 hours is a conservative number that should be enough even if the
# model changes.

HOURS_PAST = 48
WEATHER_FORECAST_HOURS_FUTURE = 6


def _update_weather_forecast(weather_task, hour):
    """
    Fetches latest weather forecast and saves it to the database.
    """
    forecast_horizon = hour + timedelta(hours=WEATHER_FORECAST_HOURS_FUTURE)
    weather_forecast = weather_task(hour, forecast_horizon)
    weather_forecast_window = weather_forecast.ix[hour:forecast_horizon]
    WeatherForecast.insert_or_replace(weather_forecast_window)


def _update_historical_data(generation_task, weather_task, hour, hours_past):
    start = hour - timedelta(hours=hours_past)
    end = hour
    generation_report = generation_task(start, end)
    weather_report = weather_task(start, end)


def prepare_forecast(historical_data_source, generation_task, weather_task, hour):
    """
    Prepare database for calculating a forecast.

    - always fetch latest weather forecast
    - maybe fetch historical data if missing
    """

    _update_weather_forecast(weather_task, hour)

    generation_reports, weather_forecasts = historical_data_source(hour, HOURS_PAST)

    if is_historical_data_present(generation_reports, weather_forecasts, HOURS_PAST):
        return

    _update_historical_data(generation_task, weather_task, hour, HOURS_PAST)
