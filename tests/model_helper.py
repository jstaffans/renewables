from datetime import timedelta
from app.model import GenerationReport, WeatherForecast


def full_historical_data(hour, hours_past):
    h = hour - timedelta(hours=hours_past)

    generation_reports = []
    weather_forecasts = []

    while h < hour:
        generation_reports.append(
            GenerationReport(timestamp=h, renewables=0.5, non_renewables=0.5)
        )
        weather_forecasts.append(
            WeatherForecast(
                timestamp=h,
                wind_speed=5.0,
                cloud_cover=0.5,
                temperature=20.0,
                pressure=1024.0,
            )
        )
        h = h + timedelta(hours=1)

    return (generation_reports, weather_forecasts)


def partial_historical_data(hour, hours_past):
    generation_reports, weather_forecasts = full_historical_data(hour, hours_past)
    generation_reports.pop()
    weather_forecasts.pop()
    return (generation_reports, weather_forecasts)
