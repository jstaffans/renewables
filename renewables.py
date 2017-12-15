from flask import Flask
from pyiso import client_factory
import click

app = Flask(__name__)


@app.cli.command()
@click.argument('control_area')
def generation(control_area):
    entso = client_factory('EU')
    generation = entso.get_generation(latest=True, control_area=control_area)

    # import json
    # print(json.dumps(generation, indent=2, default=str))
