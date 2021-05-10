from newscrawler import db
from sqlalchemy.ext.declarative import declared_attr
from functools import reduce
from newscrawler.utils import color, refactor, clamp

def average(prev_avg, x, n):
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
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)


class Article(Base):
    __tablename__ = 'article'

    url = db.Column(db.String)
    title = db.Column(db.String)
    date = db.Column(db.Date)
    byline = db.Column(db.String)
    text = db.Column(db.Text)
    pos = db.Column(db.Float)
    neu = db.Column(db.Float)
    neg = db.Column(db.Float)
    sent = db.Column(db.Float)
    compound = db.Column(db.Float)

    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'))
    agency = db.relationship('Agency',
                             primaryjoin='Article.agency_id==Agency.id',
                             backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return f'<Article {self.agency.name}: {self.title} {self.date}>'

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
        # expand the number
        num = clamp(self.sentiment, -25, 25)
        return color(num, [-25,25])

    @property
    def neutrality_color(self):
        # expand the number
        num = clamp(self.neutrality, 70, 100)
        return color(num, [70,100], color1='808080', color2='0000FF')

    @property
    def compound_color(self):
        return color(self.compound, [-100,100])


class Agency(Base):
    __tablename__ = 'agency'

    name = db.Column(db.String)
    homepage = db.Column(db.String)
    cum_sent = db.Column(db.Float, default=0.0, nullable=False)
    cum_neut = db.Column(db.Float, default=0.0, nullable=False)

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
        # expand the number
        num = clamp(self.cumulative_sentiment, -25, 25)
        return color(num, [-25,25])

    @property
    def neutrality_color(self):
        # expand the number
        num = clamp(self.cumulative_neutrality, 70, 100)
        return color(num, [70,100], color1='808080', color2='0000FF')

    def reaccumulate(self):
        self.cum_sent = 0
        for i, a in enumerate(windowed_query(self.articles, Article.sent, 1000)):
            self.cum_sent = average(self.cum_sent, a.sent, i+1)
        self.cum_neut = 0
        for i, a in enumerate(windowed_query(self.articles, Article.neu, 1000)):
            self.cum_neut = average(self.cum_neut, a.neu, i+1)
