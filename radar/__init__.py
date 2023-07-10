from flask import Flask
from .config import Config
from .blueprints.home import home_blueprint

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config_class)

    app.register_blueprint(home_blueprint)

    return app
