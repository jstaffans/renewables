from datetime import datetime, timedelta
from app.tasks.generation import generation as generation_task
from app.model import GenerationReport, WeatherForecast, is_historical_data_present


def _shift_weather_features_back(weather_report, hours):
    """
    Shift weather observations back in time. The weather observation at time t can
    then be interpreted as a forecast made at time t. A number of hours equal to the
    shift are rolled off the end of the DataFrame.
    """
    shifted = weather_report.copy()
    shifted.wind_speed = shifted.wind_speed.shift(-hours)
    shifted.temperature = shifted.temperature.shift(-hours)
    shifted.cloud_cover = shifted.cloud_cover.shift(-hours)
    shifted.pressure = shifted.pressure.shift(-hours)
    shifted = shifted[:-hours]
    return shifted


def _update_weather_forecast(weather_task, hour, hours_predict):
    """
    Fetches latest weather forecast and saves it to the database.
    """
    forecast_horizon = hour + timedelta(hours=hours_predict)
    weather_forecast = weather_task(hour, forecast_horizon + timedelta(hours=1))
    weather_forecast = _shift_weather_features_back(weather_forecast, 1)
    weather_forecast_window = weather_forecast.ix[hour:forecast_horizon]
    WeatherForecast.insert_or_replace(weather_forecast_window)


def _update_historical_data(generation_task, weather_task, hour, hours_past):
    start = hour - timedelta(hours=hours_past)
    end = hour

    generation_report = generation_task(start, end)
    weather_report = weather_task(start, end + timedelta(hours=1))
    weather_report = _shift_weather_features_back(weather_report, 1)

    GenerationReport.insert_or_replace(generation_report)
    WeatherForecast.insert_or_replace(weather_report)


def prepare_prediction(
    historical_data_source, generation_task, weather_task, model_params, hour
):
    """
    Prepare database for predicting ratio of renewable energy.

    - always fetch latest weather forecast
    - maybe fetch historical data if missing

    The hour should be in UTC.
    """

    _update_weather_forecast(weather_task, hour, model_params.hours_predict)

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
