from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from scrapy.utils.project import get_project_settings


CONNECTION_STRING = 'sqlite:///articles.db'

Base = declarative_base()


def db_connect():
    return create_engine(CONNECTION_STRING)


def create_table(engine):
    Base.metadata.create_all(engine)

def get_session():
        engine = db_connect()
        create_table(engine)
        return sessionmaker(bind=engine)()

class Article(Base):
    __tablename__ = 'article'

    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.String)
    title = sa.Column(sa.String)
    date = sa.Column(sa.String)
    byline = sa.Column(sa.String)
    text = sa.Column(sa.Text)
    pos = sa.Column(sa.Float)
    neu = sa.Column(sa.Float)
    neg = sa.Column(sa.Float)
    compound = sa.Column(sa.Float)
