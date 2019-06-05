"""
Basic infrastructures

Provides logging, DB acccess, config etc.
"""
import logging
import json
import os

# Load Flask and config
from flask import Flask
from . import settings
settings = settings.AppSettings
settings.update_from_env()
settings.initialize()

app = Flask(__name__, static_url_path=F'{settings.RELATIVE_PATH}', static_folder="dist/")
app.config.from_object(settings)


@app.route(F'{settings.RELATIVE_PATH}/', defaults={"path": "index.html"})
def index(path):
    if os.path.exists(os.path.join(os.path.join(app.static_folder, path))):
        return app.send_static_file(path)
    else:
        return 'Frontend page not built, see README to setup the app first'

# If not catch by any view, fallback to index on non-static
@app.errorhandler(404)
def page_not_found(e):
    return index('index.html'), 302
# Then fallback to static files


# setup logging
def setup_logger():
    fmt = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    loglevel = logging.INFO  # TODO: in config
    formatter = logging.Formatter(fmt=fmt)

    logging.basicConfig(format=fmt, level=loglevel)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger('metadb')
    root_logger.setLevel(loglevel)
    root_logger.addHandler(console_handler)
    return root_logger


logger = setup_logger()


# Load Flask and config
from metadash.exceptions import init_app as init_exceptions # noqa
init_exceptions(app)


# Load ORM
from flask_sqlalchemy import SQLAlchemy # noqa
db = SQLAlchemy(app)


# Load default configs
from .config import Config, load_meta # noqa
from .apis.config import Blueprint as ConfigBlueprint # noqa
defaults = os.path.abspath(os.path.join(os.path.dirname(__file__), "./config/defaults.json"))
app.register_blueprint(ConfigBlueprint, url_prefix=settings.API_PATH)
with app.app_context():
    Config.init()
with open(defaults) as default_configs:
    load_meta(json.load(default_configs))


# Load buildin models
import metadash.models.metadata # noqa


# Load plugins
from metadash.plugins import Plugins as plugins # noqa
plugins.regist(app)


# Load tasks query API
from .apis.tasks import Blueprint as tasks # noqa
app.register_blueprint(tasks, url_prefix=settings.API_PATH)


# Load Authentication API
from .apis.auth import Blueprint as login # noqa
app.register_blueprint(login, url_prefix=settings.API_PATH)


# Load Views
from metadash.apis.metadata import Blueprint as metadata # noqa
app.register_blueprint(metadata, url_prefix=settings.API_PATH)
