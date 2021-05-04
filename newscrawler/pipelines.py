# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from newscrawler.models import db_connect, create_table, Article, Agency
from sqlalchemy.orm import sessionmaker
import logging

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class NewscrawlerPipeline:
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine, autoflush=False)
        self.sid = SentimentIntensityAnalyzer()

    def process_item(self, item, spider):
        session = self.Session()
        article = Article()
        article.title = item['title']
        article.url = item['url']
        article.byline = item['byline']
        article.date = item['date']
        article.text = item['text']
        sid = self.sid.polarity_scores(article.text)
        article.pos = sid['pos']
        article.neg = sid['neg']
        article.neu = sid['neu']
        article.compound = sid['compound']

        agency = session.query(Agency).filter_by(name=item['agency']).first()
        if not agency:
            agency = Agency()
            agency.name = item['agency']
            agency.homepage = item['start']
        article.agency = agency

        exists = session.query(Article).filter_by(title=article.title).first()
        if exists:
            return item
        try:
            session.add(article)
            session.commit()
        except Exception as e:
            print(article, e)
        finally:
            session.close()

        return item
