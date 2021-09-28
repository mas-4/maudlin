import time
from datetime import date
from statistics import mean
from newscrawler import db
from sqlalchemy.ext.declarative import declared_attr
from newscrawler.utils import color, clamp, timing

def average(prev_avg, x, n):
    """Function for a streaming average"""
    return ((prev_avg *
             n + x) /
            (n + 1));


def windowed_query(q, column, windowsize):
    """"Break a Query into chunks on a given column."""

    single_entity = q.is_single_entity
    q = q.add_column(column).order_by(column)
    last_id = None

    while True:
        subq = q
        if last_id is not None:
            subq = subq.filter(column > last_id)
        chunk = subq.limit(windowsize).all()
        if not chunk:
            break
        last_id = chunk[-1][-1]
        for row in chunk:
            if single_entity:
                yield row[0]
            else:
                yield row[0:-1]


class Base(db.Model):
    """Abstract base class"""
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)


class Article(Base):
    """An article in the database"""
    # article data
    url = db.Column(db.String)
    title = db.Column(db.String)
    date = db.Column(db.Date)
    byline = db.Column(db.String)
    text = db.Column(db.Text)

    # sentiment data
    pos = db.Column(db.Float)
    neu = db.Column(db.Float)
    neg = db.Column(db.Float)
    sent = db.Column(db.Float) # pos - neg
    compound = db.Column(db.Float)

    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'))
    agency = db.relationship('Agency',
                             primaryjoin='Article.agency_id==Agency.id',
                             backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return f'<Article {self.agency.name}: {self.title} {self.date}>'

    # most of these properties are just the various datapoints turned into
    # percents because they're nicer
    @property
    def sentiment(self):
        return round(self.sent * 100, 2)

    @property
    def neutrality(self):
        return round(self.neu * 100, 2)

    @property
    def comp(self):
        return round(self.compound * 100, 2)

    @property
    def color(self):
        """A property for generating a color between red and green for the
        sentiment of the article.
        """
        num = clamp(self.sentiment, -25, 25)
        return color(num, [-25,25])

    @property
    def neutrality_color(self):
        """Same as color but for neutrality, between grey and blue"""
        num = clamp(self.neutrality, 70, 100)
        return color(num, [70,100], color1='808080', color2='0000FF')

    @property
    def compound_color(self):
        """Same as color and neutrality_color but for compound."""
        return color(self.compound, [-100,100])

    @staticmethod
    def todays_sentiment():
        """Get a mean of sentiment for all of today's articles."""
        t = time.time()
        sentiment = db.session.query(db.func.avg(Article.sent)).filter(Article.date==date.today()).all()
        timing(t, "article.todays_sentiment")
        if sentiment[0][0]:
            return round(sentiment[0][0]*100, 2)
        return 0


class Agency(Base):
    __tablename__ = 'agency'

    # Agency data
    name = db.Column(db.String)
    homepage = db.Column(db.String)

    # Cumulative sentiment and neutrality, calculated as a streaming average for
    # every new article. `reaccumulate()` recalculates these.
    cum_sent = db.Column(db.Float, default=0.0, nullable=False)
    cum_neut = db.Column(db.Float, default=0.0, nullable=False)
    last_date = db.Column(db.Date)

    def __repr__(self):
        return f'<Agency {self.name}: {self.homepage} ({self.articles.count()}) articles>'

    @property
    def cumulative_sentiment(self):
        return round(self.cum_sent*100, 2)

    @property
    def cumulative_neutrality(self):
        return round(self.cum_neut*100, 2)

    @property
    def color(self):
        num = clamp(self.cumulative_sentiment, -25, 25)
        return color(num, [-25,25])

    @property
    def neutrality_color(self):
        num = clamp(self.cumulative_neutrality, 70, 100)
        return color(num, [70,100], color1='808080', color2='0000FF')

    @property
    def todays_articles(self):
        t = time.time()
        articles = self.articles.filter(Article.date==date.today())\
            .order_by(Article.sent.desc())
        timing(t, "agency.todays_articles")
        return articles

    @property
    def todays_sentiment(self):
        """Agency sentiment across all today's articles"""
        try:
            return round(mean([a.sent for a in self.todays_articles])*100, 2)
        except:
            return 0.0

    @property
    def todays_neutrality(self):
        """Agency neutrality across all today's articles"""
        try:
            return round(mean([a.neu for a in self.todays_articles])*100, 2)
        except:
            return 0.0

    @property
    def todays_count(self):
        """Count of today's articles for the agency"""
        t = time.time()
        count = self.articles.filter(Article.date==date.today()).count()
        timing(t, "agency.todays_count")
        return count

    def reaccumulate(self):
        """Recalculate the cum_sent and cum_neut for the agency. Because of the
        size of the database, use a windowed_query in 1000 article chunks.

        NOTE: When I was running this on the raspberry pi, CNN, with exactly 234
        articles, kept getting stuck on one particular article. This is a very
        weird bug, that even when I downloaded the sql dump to my laptop and ran
        the same function it didn't reproduce. It seems specific to my raspi set
        up and that particular data structure.

        I kept the sql dump, eventual investigation might help upstream. The
        problem was that the line
        ```
            subq = subq.filter(column > last_id)
        ```
        kept returning that particular article so it windowed way past the
        actual article count.
        """
        self.cum_sent = 0
        for i, a in enumerate(windowed_query(self.articles, Article.id, 1000)):
            self.cum_sent = average(self.cum_sent, a.sent, i+1)
            if not i % 100:
                print("sentiment", self, i)
        self.cum_neut = 0
        for i, a in enumerate(windowed_query(self.articles, Article.id, 1000)):
            self.cum_neut = average(self.cum_neut, a.neu, i+1)
            if not i % 100:
                print("neutrality", self, i)
