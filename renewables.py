from flask import Flask
import click
from dateutil.parser import parse
from datetime import datetime, timedelta

from app.tasks.generation import generation as generation_task

app = Flask(__name__)

def parse_date(d):
    try:
        date = parse(d)
    except:
        raise click.BadParameter("Couldn't parse date.", param=d)
    return date

@app.cli.command()
@click.argument('control_area')
@click.option('--date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
def generation(control_area, date):
    start = parse_date(date)
    end = start + timedelta(days=1)
    result = generation_task(ba_name='EU', control_area=control_area, start=start, end=end)
    result.to_csv('generation_{:%Y-%m-%d}.csv'.format(start))
