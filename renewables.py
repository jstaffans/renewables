from flask import Flask
import click
from dateutil.parser import parse
from datetime import datetime, timedelta

from app.tasks import generation as generation_task

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
    result = generation_task('EU', control_area, start, end)
    print(result)
