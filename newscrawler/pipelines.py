from itemadapter import ItemAdapter
from newscrawler.models import Article, Agency
from newscrawler import db
import logging

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class NewscrawlerPipeline:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()

    def process_item(self, item, spider):
        article = Article.query.filter(Article.title==item['title']).first()
        created = False
        if not article:
            # article doesn't exist, create it
            article = Article()
            created = True

        article.title = item['title']
        article.url = item['url']
        article.byline = item['byline']
        article.date = item['date']
        article.text = item['text']

        sid = self.sid.polarity_scores(article.text)
        article.pos = sid['pos']
        article.neg = sid['neg']
        article.neu = sid['neu']
        article.sent = article.pos - article.neg
        article.compound = sid['compound']

        agency = Agency.query.filter_by(name=item['agency']).first()
        logging.info(agency)
        if not agency:
            agency = Agency()
            agency.name = item['agency']
            agency.homepage = item['start']
            agency.cum_sent = 0.0
            agency.cum_neut = 0.0

        article.agency = agency

        logging.info(article)

        # calculate cumulative averages
        if created:
            sent = article.pos - article.neg
            agency.cum_sent += (sent - agency.cum_sent) / agency.articles.count()
            agency.cum_neut += (article.neu - agency.cum_neut) / agency.articles.count()

        try:
            if created:
                db.session.add(article)
            db.session.commit()
            logging.info("Successfully committed")
        except Exception as e:
            logging.info(e)
            logging.info(article)
            db.session.rollback()

        return item
