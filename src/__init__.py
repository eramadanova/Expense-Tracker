"""
This module initializes the Flask application and sets up configurations.

It defines the `create_app` function to initialize Flask, set configurations,
initialize the database and register blueprints.
"""
import importlib

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import src.config as config
from src.utils_api import load_default_currency

db = SQLAlchemy()

def create_app():
    """
    Creates and configures a Flask application.

    :return: The initialized Flask application instance.
    """
    app = Flask(__name__)
    app.secret_key = 'asdfvm kfkmvkemd n'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'

    app.config.from_pyfile('../src/config.py')

    db.init_app(app)

    # from app.routes import create_blueprints
    blueprints_module = importlib.import_module('src.routes')
    for bp in blueprints_module.create_blueprints():
        app.register_blueprint(bp)

    config.DEFAULT_CURRENCY = load_default_currency()

    return app
