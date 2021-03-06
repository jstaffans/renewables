import click
import os
import pandas as pd
from dateutil.parser import parse
from datetime import datetime, timedelta
from functools import partial
from flask import Flask, render_template
from flask_webpack import Webpack

from app import create_app
from app.model import (
    csv_to_pd,
    GenerationReport,
    GenerationPrediction,
    ModelParameters,
    historical_data,
    generation_and_weather_lookback
)
from app.tasks.generation import generation as generation_task
from app.tasks.weather import weather as weather_task
from app.tasks.prediction import (
    prepare_prediction as prepare_prediction_task,
    predict as prediction_task,
)
from app.sun import sun_calendar_lookback
from app.util import hour_now


app = create_app()

webpack = Webpack()
webpack.init_app(app)


@app.route("/")
def index():
    return render_template("index.jinja2")


# Management commands, mainly for reading batches of generation data from the API


def _parse_date(d):
    try:
        date = parse(d)
    except:
        raise click.BadParameter("Couldn't parse date.", param=d)
    return date


@app.cli.command()
@click.option("--control_area", default="DE(50HzT)")
@click.option(
    "--date", default="{:%Y-%m-%d}".format(datetime.now() - timedelta(days=1))
)
@click.option("--output_dir", default=".")
def generation(control_area, date, output_dir):
    """
    Writes a generation report for a single day to a CSV file in the given directory.
    """
    start = _parse_date(date)
    end = start + timedelta(days=1)
    result = generation_task(app.config["BA_NAME"], control_area, start, end)
    filename = f"{output_dir}/generation_{start:%Y-%m-%d}.csv"
    result.to_csv(filename)
    print(f"Wrote {filename}")


@app.cli.command()
@click.option("--control_area", default="DE(50HzT)")
@click.option(
    "--start_date", default="{:%Y-%m-%d}".format(datetime.now() - timedelta(days=1))
)
@click.option("--days", default=1)
@click.option("--output_dir", default=".")
def generation_range(control_area, start_date, days, output_dir):
    """
    Outputs generation reports for a date range, one CSV report per day, to the given directory.
    Note that the timestamps of the generated report are in UTC.
    """
    start = _parse_date(start_date)

    for i in range(days):
        current = start + timedelta(days=i)
        end = current + timedelta(days=1)
        filename = f"{output_dir}/generation_{current:%Y-%m-%d}.csv"

        if os.path.isfile(filename):
            print(f"{filename} already exists, skipping")
            continue

        result = generation_task(app.config["BA_NAME"], control_area, current, end)
        result.to_csv(filename)
        print(f"Wrote {filename}")


@app.cli.command()
@click.option("--city_name", default="Berlin")
@click.option(
    "--start_date", default="{:%Y-%m-%d}".format(datetime.now() - timedelta(days=1))
)
@click.option("--days", default=1)
@click.option("--output_dir", default=".")
def environment_range(city_name, start_date, days, output_dir):
    """
    Produces a CSV file with environmental factors like weather, sunset and sundown
    in the given output directory.
    """
    start = _parse_date(start_date)
    end = start + timedelta(days=days)
    filename = f"{output_dir}/environment_{start:%Y-%m-%d}-{end:%Y-%m-%d}.csv"
    sun = sun_calendar(city_name, start, end)
    weather = weather_task(app.config["WEATHER_API_TOKEN"], city_name, start, end)
    pd.concat([sun, weather], axis=1).to_csv(filename)
    print(f"Wrote {filename}")


@app.cli.command()
@click.option("--control_area", default="DE(50HzT)")
@click.argument("input", type=click.File("rb"))
def load_generation_report(control_area, input):
    """
    Manually load a CSV generation report into the database.
    """
    data = csv_to_pd(input)
    GenerationReport.insert_or_replace(app.config["BA_NAME"], control_area, data)
    print(f"Inserted {data.count()} rows")


@app.cli.command()
@click.option("--control_area", default="DE(50HzT)")
@click.option("--city_name", default="Berlin")
@click.option("--hours_past", default=36)
@click.option("--hours_predict", default=6)
def prepare_prediction(control_area, city_name, hours_past, hours_predict):
    """
    Prepares database for forecast at the current point in time.
    """
    model = ModelParameters(hours_past, hours_predict)
    hour = hour_now()
    generation = partial(generation_task, app.config["BA_NAME"], control_area)
    weather = partial(weather_task, app.config["WEATHER_API_TOKEN"], city_name)
    prepare_prediction_task(historical_data, generation, weather, model, hour)
    print(f"Prepared database for prediction at {hour}")


@app.cli.command()
@click.option("--city_name", default="Berlin")
@click.option("--prediction_time", default=hour_now())
@click.option("--hours_past", default=27)
@click.option("--hours_predict", default=1)
def predict(city_name, prediction_time, hours_past, hours_predict):
    """
    Makes a prediction at the given point in time based on the generation and
    weather data available in the database. Stores the prediction in the database.

    By default, prediction is performed for the current hour.
    If another prediction time is used, the given time string
    is interpreted as UTC, e.g. "2018-08-08T19:00".

    hours_past must align with the pre-trained prediction model.
    """
    model = ModelParameters(hours_past, hours_predict)
    hour = (
        prediction_time
        if isinstance(prediction_time, datetime)
        else parse(prediction_time)
    )
    generation_and_weather = generation_and_weather_lookback(
        hour, model_params.hours_past
    )
    sun = sun_calendar_lookback(city_name, hour, model_params.hours_past)
    window = pd.concat([generation_and_weather, sun], axis=1)

    prediction = prediction_task(window, hour)
    print(prediction.renewables_ratio)
    # GenerationPrediction.insert_or_replace(hour, predicted_ratio)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
