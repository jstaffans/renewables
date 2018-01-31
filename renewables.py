import click
import os
import pandas as pd
from dateutil.parser import parse
from datetime import datetime, timedelta
from flask import Flask, render_template
from flask_webpack import Webpack

from app.db import db, migrate
from app.tasks.generation import generation as generation_task


webpack = Webpack()

def create_app(settings_override=None):
    app = Flask(__name__)

    params = {
        'DEBUG': True,
        'WEBPACK_MANIFEST_PATH': './build/manifest.json',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///renewables.db',
    }

    app.config.update(params)

    if settings_override:
        app.config.update(settings_override)

    db.init_app(app)
    migrate.init_app(app, db)
    webpack.init_app(app)

    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.jinja2')

# Management commands, mainly for reading batches of generation data from the API

def _parse_date(d):
    try:
        date = parse(d)
    except:
        raise click.BadParameter("Couldn't parse date.", param=d)
    return date

@app.cli.command()
@click.argument('control_area')
@click.option('--date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
def generation(control_area, date):
    start = _parse_date(date)
    end = start + timedelta(days=1)
    result = generation_task(ba_name='EU', control_area=control_area, start=start, end=end)
    filename = 'generation_{:%Y-%m-%d}.csv'.format(start)
    result.to_csv(filename)
    print('Wrote {}'.format(filename))

@app.cli.command()
@click.argument('control_area')
@click.option('--start_date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
@click.option('--days', default=1)
@click.option('--output_dir', default='.')
def generation_range(control_area, start_date, days, output_dir):
    start = _parse_date(start_date)

    for i in range(days):
        current = start + timedelta(days=i)
        end = current + timedelta(days=1)
        filename = '{}/generation_{:%Y-%m-%d}.csv'.format(output_dir, current)

        if os.path.isfile(filename):
            print('{} already exists, skipping'.format(filename))
            continue

        result = generation_task(ba_name='EU', control_area=control_area, start=current, end=end)
        result.to_csv(filename)

        print('Wrote {}'.format(filename))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
