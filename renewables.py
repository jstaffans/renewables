import click
import os
import pandas as pd
from dateutil.parser import parse
from datetime import datetime, timedelta
from flask import Flask, render_template
from flask_webpack import Webpack

from app import create_app
from app.model import csv_to_pd, insert_generation_report
from app.tasks.generation import generation as generation_task
from app.tasks.sun import sun_calendar as sun_calendar_task


app = create_app()

webpack = Webpack()
webpack.init_app(app)

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
@click.option('--control_area', default='DE(50HzT)')
@click.option('--date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
@click.option('--output_dir', default='.')
def generation(control_area, date, output_dir):
    """
    Writes a generation report for a single day to a CSV file in the given directory.
    """
    start = _parse_date(date)
    end = start + timedelta(days=1)
    result = generation_task(app.config['BA_NAME'], control_area, start, end)
    filename = f'{output_dir}/generation_{start:%Y-%m-%d}.csv'
    result.to_csv(filename)
    print(f'Wrote {filename}')

@app.cli.command()
@click.option('--control_area', default='DE(50HzT)')
@click.option('--start_date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
@click.option('--days', default=1)
@click.option('--output_dir', default='.')
def generation_range(control_area, start_date, days, output_dir):
    """
    Outputs generation reports for a date range, one CSV report per day, to the given directory.
    """
    start = _parse_date(start_date)

    for i in range(days):
        current = start + timedelta(days=i)
        end = current + timedelta(days=1)
        filename = f'{output_dir}/generation_{current:%Y-%m-%d}.csv'

        if os.path.isfile(filename):
            print(f'{filename} already exists, skipping')
            continue

        result = generation_task(app.config['BA_NAME'], control_area, current, end)
        result.to_csv(filename)
        print(f'Wrote {filename}')

@app.cli.command()
@click.option('--city_name', default='Berlin')
@click.option('--start_date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
@click.option('--days', default=1)
@click.option('--output_dir', default='.')
def environment_range(city_name, start_date, days, output_dir):
    """
    Produces a CSV file with environmental factors like weather, sunset and sundown
    in the given output directory.
    """
    start = _parse_date(start_date)
    end = start + timedelta(days=days)
    filename = f'{output_dir}/environment_{start:%Y-%m-%d}-{end:%Y-%m-%d}.csv'
    result = sun_calendar_task(city_name, start, end)
    result.to_csv(filename)
    print(f'Wrote {filename}')

@app.cli.command()
@click.option('--control_area', default='DE(50HzT)')
@click.argument('input', type=click.File('rb'))
def load_generation_report(control_area, input):
    data = csv_to_pd(input)
    insert_generation_report(app.config['BA_NAME'], control_area, data)
    print(f'Inserted {data.count()} rows')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
