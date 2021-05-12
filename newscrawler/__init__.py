import os, logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flaskext.markdown import Markdown
from flask_sqlalchemy import SQLAlchemy
from sassutils.wsgi import SassMiddleware
from newscrawler.config import Config
from newscrawler import utils
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
md = Markdown(app, safe_mode=True, output_format='html4')
app.wsgi_app = SassMiddleware(
    app.wsgi_app,
    { 'newscrawler': ('static/sass', 'static/css', '/static/css') })

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
app.jinja_env.globals.update(round=round)

from newscrawler import routes, models, errors
