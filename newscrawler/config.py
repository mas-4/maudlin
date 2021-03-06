import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
try:
    load_dotenv()
    print("Dotfiles loaded")
except:
    pass


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')
    print(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SCRAPY_URL = os.environ.get('SCRAPY_URL') or \
        'http://localhost:6800'
    SCRAPY_USR = os.environ.get('SCRAPY_USR') or 'Yeah right.'
    SCRAPY_PWD = os.environ.get('SCRAPY_PWD') or "Seriously, c'mon"

    CACHE_TYPE = "SimpleCache"  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 300
    CELERY_BROKER_URL = 'redis://localhost/1'

    WORDCLOUD_URL = 'https://maudlin.standingwater.io/wc/wordcloud.png'
    LogFailPath = '/failures.txt'
