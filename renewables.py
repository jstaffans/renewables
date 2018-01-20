import click
import os
import pandas as pd
from dateutil.parser import parse
from datetime import datetime, timedelta
from flask import Flask

from app.tasks.generation import generation as generation_task

app = Flask(__name__)

def parse_date(d):
    try:
        date = parse(d)
    except:
        raise click.BadParameter("Couldn't parse date.", param=d)
    return date

# Management commands, mainly for reading batches of generation data from the API

@app.cli.command()
@click.argument('control_area')
@click.option('--date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
def generation(control_area, date):
    start = parse_date(date)
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
    start = parse_date(start_date)

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
