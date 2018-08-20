import itertools
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
from keras.models import load_model
from sklearn.externals import joblib
from app.tasks.generation import generation as generation_task
from app.model import (
    GenerationReport,
    GenerationPrediction,
    WeatherForecast,
    is_historical_data_present,
    generation_and_weather_window,
    MODEL_FEATURES,
)


@lru_cache()
def _load_model():
    return (
        load_model(os.path.join(os.path.dirname(__file__), "model_non_overlap_24.h5")),
        joblib.load(os.path.join(os.path.dirname(__file__), "scaler.save")),
    )


def _predict(window):
    model, scaler = _load_model()
    pred_x = window[MODEL_FEATURES].as_matrix()
    pred_x = scaler.transform(pred_x)
    pred_x = np.array([pred_x])
    pred_y = model.predict(pred_x)
    return pred_y.flatten()[0]


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
    """
    Retrieves generation reports and weather data and updates DB.
    """
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


def predict(sun_calendar, model_params, hour):
    """
    Makes a prediction for hour+1. Assumes DB contains enough data to construct
    a prediction window.

    Raises ValueError if not enough data is available to make a prediction.
    """
    generation_and_weather = generation_and_weather_window(
        hour, model_params.hours_past
    )
    sun = sun_calendar(hour, model_params.hours_past)
    window = pd.concat([generation_and_weather, sun], axis=1)

    predicted_ratio = _predict(window)

    return GenerationPrediction(timestamp=hour, renewables_ratio=predicted_ratio)
