import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
try:
    load_dotenv()
except:
    pass


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCRAPY_URL = os.environ.get('SCRAPY_URL') or \
        'http://localhost:6800'

    CACHE_TYPE = "SimpleCache"  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 300
    CELERY_BROKER_URL = 'redis://localhost/1'
