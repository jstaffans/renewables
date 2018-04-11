from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app(settings_override=None):
    app = Flask(__name__, template_folder='../templates')

    params = {
        'DEBUG': True,
        'WEBPACK_MANIFEST_PATH': '../build/manifest.json',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///renewables.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }

    app.config.update(params)

    if settings_override:
        app.config.update(settings_override)

    db.init_app(app)
    migrate.init_app(app, db)

    return app
