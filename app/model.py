from collections import namedtuple
from datetime import datetime, timedelta
import pandas as pd

from app import db


# ENTSO-E mappings
RENEWABLES = ["wind", "hydro", "solar", "biomass"]
NON_RENEWABLES = ["coal", "fossil", "natgas", "oil", "other", "refuse"]

ModelParameters = namedtuple("ModelParameters", "hours_past hours_predict")


def csv_to_pd(filename):
    """Reads a generation report from a CSV file, returns a Pandas DataFrame."""
    return pd.read_csv(filename, parse_dates=True, index_col="timestamp")


def _public_vars(instance):
    return {k: v for k, v in vars(instance).items() if not k.startswith("_")}


class GenerationReport(db.Model):
    __table_args__ = {"info": {"without_rowid": True}}
    timestamp = db.Column(db.DateTime, primary_key=True)
    renewables = db.Column(db.Float, nullable=False)
    non_renewables = db.Column(db.Float, nullable=False)

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
            row["renewables"] = v["renewables"]
            row["non_renewables"] = v["non_renewables"]
            rows.append(row)

        db.engine.execute(
            GenerationReport.__table__.insert().prefix_with("OR REPLACE"), rows
        )

    @property
    def renewables_ratio(self):
        return self.renewables / (self.renewables + self.non_renewables)

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        ratio = f"renewables_ratio={self.renewables_ratio:.2f}"
        return f"<GenerationReport {timestamp} {ratio}>"


class GenerationPrediction(db.Model):
    __table_args__ = {"info": {"without_rowid": True}}
    timestamp = db.Column(db.DateTime, primary_key=True)
    renewables_ratio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        ratio = f"renewables_ratio={self.renewables_ratio:.2f}"
        return f"<GenerationPrediction {timestamp} {ratio}>"


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


def generation_predictions(start, hours):
    return (
        GenerationPrediction.query.filter(GenerationPrediction.timestamp >= start)
        .order_by(GenerationPrediction.timestamp)
        .limit(hours)
        .all()
    )


def is_historical_data_present(generation_reports, weather_forecasts, hours_past):
    """
    Depending on the model used, we rely on some historical data
    when the generation forecast is done. This function checks that we
    have the necessary data.
    """

    return (
        len(generation_reports) >= hours_past and len(weather_forecasts) >= hours_past
    )


def generation_and_weather_window(hour, hours_past):
    """
    (Historical) data which forms the base for a prediction. The prediction is made
    for the next hour relative to the "hour" parameter.

    To support making predictions more than hour into the future, generation data is first
    retrieved from generation reports (ie actual data). If that's not enough, we attempt to
    retrieve a generation prediction for the given hour.

    Besides generation reports/forecasts, weather data is also part of the prediction window.

    Raises ValueError if not enough data can be gathered to fill a window.

    Returns a Pandas DataFrame that is ready to be plugged in to the prediction model.
    """

    generation, weather = historical_data(hour, hours_past)

    missing_hours = hours_past - len(generation)

    if missing_hours == hours_past:
        raise ValueError("Not enough data to construct prediction window")

    if missing_hours > 0:
        predictions = generation_predictions(generation[-1].timestamp, missing_hours)
        generation = generation + predictions

    if min(len(generation), len(weather)) < hours_past:
        raise ValueError("Not enough data to construct prediction window")

    window = pd.concat(
        [
            pd.DataFrame([_public_vars(gr) for gr in generation]).set_index(
                "timestamp"
            ),
            pd.DataFrame([_public_vars(wf) for wf in weather]).set_index("timestamp"),
        ],
        axis=1,
    )

    window["renewables_ratio"] = window.apply(
        lambda row: row["renewables_ratio"]
        if "renewables_ratio" in row and row["renewables_ratio"] > 0
        else row["renewables"] / (row["renewables"] + row["non_renewables"]),
        axis=1,
    )

    window.drop(["renewables", "non_renewables"], axis=1, inplace=True)

    return window
