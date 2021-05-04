from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr

import sqlalchemy as sa
from scrapy.utils.project import get_project_settings
import logging

import os
from dotenv import load_dotenv
load_dotenv()

CONNECTION_STRING = os.environ.get('DB_URI', 'sqlite:///articles.db')
logging.info("Connection string:", CONNECTION_STRING)


metadata = MetaData()

class Base_:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, primary_key=True)

Base = declarative_base(cls=Base_, metadata=metadata)

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

    url = sa.Column(sa.String)
    title = sa.Column(sa.String)
    date = sa.Column(sa.String)
    byline = sa.Column(sa.String)
    text = sa.Column(sa.Text)
    pos = sa.Column(sa.Float)
    neu = sa.Column(sa.Float)
    neg = sa.Column(sa.Float)
    compound = sa.Column(sa.Float)

    agency_id = sa.Column(sa.Integer, sa.ForeignKey('agency.id'))

    def __repr__(self):
        return f'<Article {self.agency.name}: {self.title} {self.date}>'


class Agency(Base):
    __tablename__ = 'agency'

    name = sa.Column(sa.String)
    homepage = sa.Column(sa.String)
    articles = relationship('Article', backref='agency')

    def __repr__(self):
        return f'<Agency {self.name}: {self.homepage} ({len(self.articles)}) articles>'


def db_connect():
    return create_engine(CONNECTION_STRING)


def create_table(engine):
    Base.metadata.create_all(engine)


def get_session():
        engine = db_connect()
        create_table(engine)
        return sessionmaker(bind=engine)()
