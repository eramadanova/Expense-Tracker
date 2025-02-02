from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asdfvm kfkmvkemd n'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Зареждане на конфигурацията
    app.config.from_pyfile('../config.py')

    # Инициализиране на разширенията
    db.init_app(app)

    from app.routes import create_blueprints
    # Регистрация на blueprint-ове
    for bp in create_blueprints():
        app.register_blueprint(bp)

    return app
