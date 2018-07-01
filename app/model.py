from collections import namedtuple
from datetime import datetime, timedelta
import pandas as pd

from app import db


# ENTSO-E mappings
RENEWABLES = ["wind", "hydro", "solar", "biomass"]
NON_RENEWABLES = ["coal", "fossil", "natgas", "oil", "other", "refuse"]

ModelParameters = namedtuple("ModelParameters", "hours_past hours_forecast")


def csv_to_pd(filename):
    """Reads a generation report from a CSV file, returns a Pandas DataFrame."""
    return pd.read_csv(filename, parse_dates=True, index_col="timestamp")


class GenerationReport(db.Model):
    __table_args__ = {"info": {"without_rowid": True}}
    timestamp = db.Column(db.DateTime, primary_key=True)
    renewables_ratio = db.Column(db.Float, nullable=False)

    @staticmethod
    def insert_or_replace(report):
        """
        Inserts a generation report in the form a Pandas DataFrame into the database.
        """
        assert isinstance(report, pd.DataFrame)

        rows = []
        dict_report = report.to_dict("index")
        for k, v in dict_report.items():
            row = {}
            row["timestamp"] = k.to_pydatetime()
            row["renewables_ratio"] = v["renewables"] / (v["renewables"] + v["non_renewables"])
            rows.append(row)

        db.engine.execute(
            GenerationReport.__table__.insert().prefix_with("OR REPLACE"), rows
        )

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        ratio = f"renewables_ratio={self.renewables_ratio:.2f}"
        return f"<GenerationReport {timestamp} {renewables_ratio}>"


class GenerationPrediction(db.Model):
    __table_args__ = {"info": {"without_rowid": True}}
    timestamp = db.Column(db.DateTime, primary_key=True)
    renewables_ratio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        ratio = f"renewables_ratio={self.renewables_ratio:.2f}"
        return f"<GenerationPrediction {timestamp} {renewables_ratio}>"


class WeatherForecast(db.Model):
    """
    Forecast at timestamp t for timestamp t+1 hour.
    """

    __table_args__ = {"info": {"without_rowid": True}}
    timestamp = db.Column(db.DateTime, primary_key=True)
    wind_speed = db.Column(db.Float, nullable=False)
    cloud_cover = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)

    @staticmethod
    def insert_or_replace(report):
        """
        Inserts a weather forecast in the form a Pandas DataFrame into the database.
        """
        assert isinstance(report, pd.DataFrame)

        rows = []
        dict_report = report.to_dict("index")
        for k, v in dict_report.items():
            row = {}
            row["timestamp"] = k.to_pydatetime()
            row["wind_speed"] = v["wind_speed"]
            row["cloud_cover"] = v["cloud_cover"]
            row["temperature"] = v["temperature"]
            row["pressure"] = v["pressure"]
            rows.append(row)

        db.engine.execute(
            WeatherForecast.__table__.insert().prefix_with("OR REPLACE"), rows
        )

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        temperature = f"temperature={self.temperature:.1f}"
        return f"<WeatherForecast {timestamp} {temperature}>"


def historical_data(hour, hours_past):
    """
    Returns a tuple of GenerationReport and WeatherForecast lists
    representing historical data looking back from the given hour.
    """

    generation_reports = (
        GenerationReport.query.filter(
            GenerationReport.timestamp >= hour - timedelta(hours=hours_past)
        )
        .order_by(GenerationReport.timestamp)
        .all()
    )

    weather_forecasts = (
        WeatherForecast.query.filter(
            WeatherForecast.timestamp >= hour - timedelta(hours=hours_past)
        )
        .order_by(WeatherForecast.timestamp)
        .all()
    )

    return (generation_reports, weather_forecasts)


def is_historical_data_present(generation_reports, weather_forecasts, hours_past):
    """
    Depending on the model used, we rely on some historical data
    when the generation forecast is done. This function checks that we
    have the necessary data.
    """

    return (
        len(generation_reports) >= hours_past and len(weather_forecasts) >= hours_past
    )
