from newscrawler import db
from sqlalchemy.ext.declarative import declared_attr

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
    compound = db.Column(db.Float)

    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'))
    agency = db.relationship('Agency',
                             primaryjoin='Article.agency_id==Agency.id',
                             backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return f'<Article {self.agency.name}: {self.title} {self.date}>'

    @property
    def sentiment(self):
        return round((self.pos - self.neg) * 100, 2)

    @property
    def neutrality(self):
        return round(self.neu * 100, 2)

    @property
    def color(self):
        h = (self.sentiment*155) / 100
        h += 100
        h = abs(h)
        d = format(int(h), 'x')
        d = d.zfill(2)
        if self.sentiment > 0:
            color = f'00{d}00'
        else:
            color = f'{d}0000'
        return color


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
