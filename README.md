Berlin Renewables
=================

## Development

### Environment variables

```
FLASK_APP=renewables.py
ENTSOe_SECURITY_TOKEN=<token>
RENEWABLES_DATABASE_URI=sqlite:////...   # absolute path to sqlite file
RENEWABLES_CONFIG=app.DevelopmentConfig  # change to app.ProductionConfig for prod
WEATHER_API_TOKEN=<token>                # dark sky api token
```

### Installing

You should be running in a virtual environment.

```
$> make install
```

### Running tests

```
$> make test
```

### Migrations

See [Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate). 

## License

Copyright © 2018 Johannes Staffans

This software is distributed under the [MIT license](https://opensource.org/licenses/MIT).
