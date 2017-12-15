from flask import Flask
from pyiso import client_factory
import click
rom dateutil.parser import parse
from datetime import datetime, timedelta


app = Flask(__name__)

def parse_date(d):
    try:
        date = parse(d)
    except:
        raise click.BadParameter("Couldn't parse date.", param=d)
    return date

@app.cli.command()
@click.option('--date', default='{:%Y-%m-%d}'.format(datetime.now() - timedelta(days=1)))
@click.argument('control_area')
def generation(date, control_area):
    entso = client_factory('EU')
    start = parse_date(date)
    end = start + timedelta(days=1)
    generation = entso.get_generation(latest=True, control_area=control_area, start_at=start, end_at=end)

    import json
    print(json.dumps(generation, indent=2, default=str))
