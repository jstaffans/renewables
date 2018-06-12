from datetime import datetime
import pandas as pd

from app import db


# ENTSO-E mappings
RENEWABLES = ["wind", "hydro", "solar", "biomass"]
NON_RENEWABLES = ["coal", "fossil", "natgas", "oil", "other", "refuse"]


def csv_to_pd(filename):
    """Reads a generation report from a CSV file, returns a Pandas DataFrame."""
    return pd.read_csv(filename, parse_dates=True, index_col="timestamp")


class GenerationReport(db.Model):
    __table_args__ = {"info": {"without_rowid": True}}
    ba_name = db.Column(db.String, primary_key=True)
    control_area = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)
    renewables = db.Column(db.Float, nullable=False)
    non_renewables = db.Column(db.Float, nullable=False)

    @staticmethod
    def insert(ba_name, control_area, report):
        """
        Inserts a generation report in the form a Pandas DataFrame into the database.
        """
        assert isinstance(report, pd.DataFrame)

        rows = []
        dict_report = report.to_dict("index")
        for k, v in dict_report.items():
            row = {}
            row["ba_name"] = ba_name
            row["control_area"] = control_area
            row["timestamp"] = k.to_pydatetime()
            row["renewables"] = v["renewables"]
            row["non_renewables"] = v["non_renewables"]
            rows.append(row)

        db.engine.execute(GenerationReport.__table__.insert().prefix_with("OR REPLACE"), rows)

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        renewables = f"renewables={self.renewables:.2f}"
        non_renewables = f"non_renewables={self.non_renewables:.2f}"
        return f"<GenerationReport {timestamp} {renewables} {non_renewables}>"


class WeatherForecast(db.Model):
    """
    Forecast at timestamp t for timestamp t+1 hour.
    """

    __table_args__ = {"info": {"without_rowid": True}}
    city_name = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)
    wind_speed = db.Column(db.Float, nullable=False)
    cloud_cover = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)

    @staticmethod
    def insert(city_name, report):
        """
        Inserts a weather forecast in the form a Pandas DataFrame into the database.
        """
        assert isinstance(report, pd.DataFrame)

        rows = []
        dict_report = report.to_dict("index")
        for k, v in dict_report.items():
            row = {}
            row["city_name"] = city_name
            row["timestamp"] = k.to_pydatetime()
            row["wind_speed"] = v["wind_speed"]
            row["cloud_cover"] = v["cloud_cover"]
            row["temperature"] = v["temperature"]
            row["pressure"] = v["pressure"]
            rows.append(row)

        db.engine.execute(WeatherForecast.__table__.insert().prefix_with("OR REPLACE"), rows)

    def __repr__(self):
        timestamp = f"timestamp='{self.timestamp:%Y-%m-%d %H:%M}'"
        city_name = f"city_name='{self.city_name}'"
        temperature = f"temperature={self.temperature:.1f}"
        return f"<GenerationReport {timestamp} {city_name} {temperature}>"
