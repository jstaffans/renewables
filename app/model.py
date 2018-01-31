from app.db import db


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
