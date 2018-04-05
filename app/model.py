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

    def __repr__(self):
        timestamp = '{:%Y-%m-%d %H:%M}'.format(self.timestamp)
        renewables = '{:.2f}'.format(self.renewables)
        non_renewables = '{:.2f}'.format(self.non_renewables)
        return f'<GenerationReport timestamp=\'{timestamp}\' renewables={renewables} non_renewables={non_renewables}>'
