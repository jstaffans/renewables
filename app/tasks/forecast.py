from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast, is_historical_data_present


def _update_weather_forecast(weather_task, hour, hours_forecast):
    """
    Fetches latest weather forecast and saves it to the database.
    """
    forecast_horizon = hour + timedelta(hours=hours_forecast)
    weather_forecast = weather_task(hour, forecast_horizon)
    weather_forecast_window = weather_forecast.ix[hour:forecast_horizon]
    WeatherForecast.insert_or_replace(weather_forecast_window)


def _update_historical_data(generation_task, weather_task, hour, hours_past):
    start = hour - timedelta(hours=hours_past)
    end = hour

    generation_report = generation_task(start.replace(hour=0), end)
    weather_report = weather_task(start, end)

    GenerationReport.insert_or_replace(generation_report)
    WeatherForecast.insert_or_replace(weather_report)


def prepare_forecast(
    historical_data_source, generation_task, weather_task, hour, model_params
):
    """
    Prepare database for calculating a forecast.

    - always fetch latest weather forecast
    - maybe fetch historical data if missing

    The hour should be in UTC.
    """

    _update_weather_forecast(weather_task, hour, model_params.hours_forecast)

    generation_reports, weather_forecasts = historical_data_source(
        hour, model_params.hours_past
    )

    if is_historical_data_present(
        generation_reports, weather_forecasts, model_params.hours_past
    ):
        return

    _update_historical_data(
        generation_task, weather_task, hour, model_params.hours_past
    )
