import math
import statistics
import io
import string
import time
from datetime import date
from flask import render_template, send_file, request, url_for
from sqlalchemy import func
from newscrawler import app, db
from newscrawler.models import Agency, Article
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


def average(agency, sent, neut):
    """Create a cumulative average for all articles to a given agency."""
    if not hasattr(agency, 'count'):
        agency.count = 1
        agency.sent = 0
        agency.neut = 0
    agency.sent += (sent - agency.sent) / agency.count
    agency.neut += (neut - agency.neut) / agency.count


@app.route('/')
def index():
    """Generates an index of today's articles, sorted by sentiment, colored by
    sentiment.
    """
    articles = Article.query.filter(Article.date==date.today()).all()
    structure = {}
    for article in articles:
        average(article.agency, article.sentiment, article.neutrality)
        if article.agency in structure:
            structure[article.agency].append(article)
        else:
            structure[article.agency] = [article]
    for agency in structure.keys():
        agency.sent = round(agency.sent, 2)
        agency.neut = round(agency.neut, 2)
        structure[agency].sort(key=lambda l: l.sentiment, reverse=True)
    overall = round(statistics.mean([a.sentiment for a in articles]), 2)
    return render_template('index.html', count=len(articles),
                           dbcount=Article.query.count(),
                           structure=structure, overall=overall)


@app.route('/agencies')
def agencies():
    sort = request.args.get('sort', default='Name')
    sorts = {
        'Name': Agency.query.order_by(Agency.name),
        'Sentiment': Agency.query.order_by(Agency.cum_sent.desc()),
        'Neutrality': Agency.query.order_by(Agency.cum_neut.desc()),
        'Articles': (Agency.query.join(Article).group_by(Agency.id)
                        .order_by(db.func.count(Article.id).desc())),
    }
    agencies = sorts[sort].all()
    return render_template('agencies.html', agencies=agencies, sorts=sorts.keys())


@app.route('/agency/<agency>')
def agency(agency):
    agency = Agency.query.filter(Agency.name == agency).first_or_404()
    return render_template('agency.html', agency=agency, Article=Article)


stopwords = list(STOPWORDS)
# clean some default words
stopwords.extend(['say', 'said', 'says', "n't", 'Mr', 'Ms', 'Mrs'])
# strip stray letters
stopwords.extend([l for l in string.ascii_lowercase + string.ascii_uppercase])
# Parts of Speech to keep
POS = [
    'FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'RB',
    'RBR', 'RBS', 'RP', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VNP', 'VBZ']

@app.route('/agency/<agency>/wordcloud')
def agencywordcloud(agency):

    # Make text
    t = time.time()
    agency = Agency.query.filter(Agency.name == agency).first_or_404()
    text = []
    articles = agency.articles.filter(Article.date==date.today()).all()
    if not articles:
        articles = agency.articles.order_by(Article.date.desc()).limit(15).all()

    for article in articles:
        text.append(article.text)
    text = ' '.join(text)
    tokenized = nltk.word_tokenize(text)
    tokenized = nltk.pos_tag(tokenized)
    text = []
    for token in tokenized:
        if token[1] in POS:
            text.append(token[0])
    text = ' '.join(text)
    app.logger.info(f"{time.time()-t}s for generating text")

    # Make wordcloud
    t = time.time()
    wordcloud = WordCloud(
        width=200, height=113, background_color='white',
        stopwords=stopwords, scale=5)\
        .generate(text).to_array()
    app.logger.info(f"{time.time()-t}s for generating wordcloud")

    # Make image
    t = time.time()
    img = Image.fromarray(wordcloud.astype('uint8'))
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)
    app.logger.info(f"{time.time()-t}s for generating image")

    return send_file(file_object, mimetype='image/png')


@app.route('/articles')
def articles():
    page = int(request.args.get('page', default='1'))
    sort = request.args.get('sort', default='date')
    direction = request.args.get('direction', default='asc')
    per_page = int(request.args.get('per_page', default='50'))
    per_pages = [10, 25, 50, 100, 250, 500]
    sorts = {
        'title': Article.title,
        'date': Article.date,
        'byline': Article.byline,
        'pos': Article.pos,
        'neg': Article.neg,
        'neu': Article.neu,
        'compound': Article.compound,
    }
    pages = list(range(1, math.ceil(Article.query.count() / 50)))
    arts = Article.query\
        .order_by(getattr(sorts[sort], direction, 'asc')())\
        .filter(Article.agency!=None)\
        .paginate(page, per_page, True)
    return render_template('articles.html', articles=arts.items, pages=pages,
                           sort=sort, page=page, direction=direction,
                           per_page=per_page, per_pages=per_pages)
