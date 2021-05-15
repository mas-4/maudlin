import re
from itemadapter import ItemAdapter
from newscrawler.models import Article, Agency, average
from newscrawler import db
import logging

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class NewscrawlerPipeline:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()

    def process_item(self, item, spider):
        # check if the article exists by its url or its title. Still might get
        # dupes. Breitbart uses different urls for the same article, and
        # sometimes agencies change the title over time.
        if not item['text']:
            logging.info("No text")
            logging.info(item['url'])
            return item
        if not item['date']:
            logging.info("No date")
            logging.info(item['date'])
            return item
        article = (Article.query.filter(Article.url==item['url']).first() or
                   Article.query.filter(Article.title==item['title']).first())
        created = False

        if not article:
            # article doesn't exist, create it
            article = Article()
            created = True

        # article data
        article.title = item['title'].replace('\xa0', '')
        article.url = item['url']
        article.byline = re.sub(re.compile('by', re.IGNORECASE), '', item['byline']).replace('\xa0', '') if hasattr(item, 'byline') and item['byline'] else None
        article.date = item['date']
        article.text = item['text']

        sid = self.sid.polarity_scores(article.text)
        article.pos = sid['pos']
        article.neg = sid['neg']
        article.neu = sid['neu']
        article.sent = article.pos - article.neg
        article.compound = sid['compound']

        agency = Agency.query.filter_by(name=item['agency']).first()
        if not agency:
            agency = Agency()
            agency.name = item['agency']
            # because it's a running average the
            # first data point is just this article.
            agency.cum_sent = article.sent
            agency.cum_neut = article.neu

        # update homepage if we change a thing
        agency.homepage = item['start']

        article.agency = agency

        # calculate cumulative averages
        if created:
            sent = article.pos - article.neg
            # special streaming average method I found on the internet and
            # can't find now
            count = agency.articles.count()
            agency.cum_sent = average(agency.cum_sent, sent, count)
            agency.cum_neut = average(agency.cum_neut, article.neu, count)

        try:
            if created:
                logging.info("New article created:" + repr(article))
                db.session.add(article)
            db.session.commit()
            logging.info("Successfully committed:" + repr(article))
        except Exception as e:
            logging.info(e)
            logging.info(article)
            db.session.rollback()

        return item
