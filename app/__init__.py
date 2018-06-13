import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite://:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BA_NAME = "EU"
    CITY_NAME = "Berlin"
    WEATHER_API_TOKEN = os.environ.get("WEATHER_API_TOKEN")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:////var/sqlite/renewables.db"


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("RENEWABLES_DATABASE_URI")
    WEBPACK_MANIFEST_PATH = "../build/manifest.json"
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test_renewables.db"
    TESTING = True


def create_app(config=os.environ.get("RENEWABLES_CONFIG")):
    app = Flask(__name__, template_folder="../templates")

    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    return app
