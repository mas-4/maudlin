import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from newscrawler.config import Config
from newscrawler import utils

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/newscrawler.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Newscrawler startup')
    app.logger.info(Config.SQLALCHEMY_DATABASE_URI)

app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(color=utils.color)
app.jinja_env.globals.update(clamp=utils.clamp)

from newscrawler import routes, models, errors
