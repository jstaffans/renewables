from datetime import datetime
import pandas as pd

from app import db


def csv_to_pd(filename):
    """Reads a generation report from a CSV file, returns a Pandas DataFrame."""
    data = pd.read_csv(filename, parse_dates=True, index_col='timestamp')
    # data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data

# ENTSO-E mappings
RENEWABLES = ['wind', 'hydro', 'solar', 'biomass']
NON_RENEWABLES = ['coal', 'fossil', 'natgas', 'oil', 'other', 'refuse']

class GenerationReport(db.Model):
    __table_args__ = {'info': {'without_rowid': True}}
    ba_name = db.Column(db.String, primary_key=True)
    control_area = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)
    renewables = db.Column(db.Float, nullable=False)
    non_renewables = db.Column(db.Float, nullable=False)

    def __repr__(self):
        timestamp = '{:%Y-%m-%d %H:%M}'.format(self.timestamp)
        renewables = '{:.2f}'.format(self.renewables)
        non_renewables = '{:.2f}'.format(self.non_renewables)
        return f'<GenerationReport timestamp=\'{timestamp}\' renewables={renewables} non_renewables={non_renewables}>'

def insert_generation_report(ba_name, control_area, report):
    """
    Inserts a generation report in the form a Pandas DataFrame into the database.
    """
    assert isinstance(report, pd.DataFrame)

    rows = []
    dict_report = report.to_dict('index')
    for k, v in dict_report.items():
        row = {}
        row['ba_name'] = ba_name
        row['control_area'] = control_area
        row['timestamp'] = k.to_pydatetime()
        row['renewables'] = v['renewables']
        row['non_renewables'] = v['non_renewables']
        rows.append(row)

    db.engine.execute(GenerationReport.__table__.insert(), rows)
