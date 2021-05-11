import math, io, string, time, os
import requests as rq
from datetime import date
from flask import (render_template, send_file, request, current_app, abort,
                   url_for)
from newscrawler import app, db
from newscrawler.models import Agency, Article
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


def timing(t, task):
    """Helper function for timing tasks"""
    now = time.time()
    app.logger.info(f"{now-t} for {task}.")
    return now


@app.route('/')
def index():
    """Generates an index of today's articles, sorted by sentiment, colored by
    sentiment.
    """
    t = time.time()
    sort = request.args.get('sort', default='Name')
    sorts = {
        'Name': Agency.query.order_by(Agency.name),
        'Articles': (Agency.query.join(Article)
                     .filter(Article.date==date.today()).group_by(Agency.id)
                     .order_by(db.func.count(Article.id).desc())),
        'Cumulative Sentiment': Agency.query.order_by(Agency.cum_sent.desc()),
        'Cumulative Neutrality': Agency.query.order_by(Agency.cum_neut.desc()),
    }
    page = request.args.get('page', default=1)
    try:
        page = int(page)
    except:
        abort(404)
    PER_PAGE = 5
    pages = list(range(1, math.ceil(Agency.query.count() / PER_PAGE)+1))
    t = timing(t, "getting sorts and pages")

    jobs = rq.get(current_app.config['SCRAPY_URL'] + '/listjobs.json?project=newscrawler')
    try:
        jobs = jobs.json()
    except Exception as e:
        app.logger.info(e)
        jobs = {'running': []}
    t = timing(t, "getting jobs")

    try:
        agencies = sorts[sort].paginate(page, PER_PAGE)
    except KeyError:
        abort(404)
    t = timing(t, "getting articles")

    html = render_template(
        'index.html',
        count=Article.query.filter(Article.date==date.today()).count(),
        dbcount=Article.query.count(),
        agencies=agencies.items,
        sorts=sorts, sort=sort, pages=pages, page=page,
        overall=Article.todays_sentiment(), running=jobs['running'])
    timing(t, "rendering template")
    return html


@app.route('/agencies')
def agencies():
    """List of all agencies"""
    sort = request.args.get('sort', default='Name')
    sorts = {
        'Name': Agency.query.order_by(Agency.name),
        'Sentiment': Agency.query.order_by(Agency.cum_sent.desc()),
        'Neutrality': Agency.query.order_by(Agency.cum_neut.desc()),
        'Articles': (Agency.query.join(Article).group_by(Agency.id)
                        .order_by(db.func.count(Article.id).desc())),
    }
    agencies = sorts[sort].all()
    return render_template('agencies.html', agencies=agencies,
                           sorts=sorts.keys(), sort=sort)


@app.route('/agency/<agency>')
def agency(agency):
    """Data for a particular agency"""
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
    """Generate a wordcloud for today's articles, or the last 15 articles"""
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
    t = timing(t, "generating texts")

    # Make wordcloud
    wordcloud = WordCloud(
        width=200, height=113, background_color='white',
        stopwords=stopwords, scale=5)\
        .generate(text).to_array()
    t = timing(t, "generating wordcloud")

    # Make image
    img = Image.fromarray(wordcloud.astype('uint8'))
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)
    timing(t, "generating image")

    return send_file(file_object, mimetype='image/png')


def pagination(c, m):
    current = c
    last = m
    delta = 2
    left = current - delta
    right = current + delta + 1
    rng = []
    rangeWithDots = []
    l = None

    for i in range(1, last+1):
        if i == 1 or i == last or i >= left and i < right:
            rng.append(i)

    for i in rng:
        if l:
            if i - l == 2:
                rangeWithDots.append(l + 1)
            elif i - l != 1:
                rangeWithDots.append('...')
        rangeWithDots.append(i)
        l = i

    return rangeWithDots


@app.route('/articles')
def articles():
    """A table of all articles"""
    page = request.args.get('page', default='1')
    try:
        page = int(page)
    except:
        abort(404)
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
    maxpages = math.ceil(Article.query.count() / per_page)
    pages = pagination(page, maxpages)
    arts = Article.query\
        .order_by(getattr(sorts[sort], direction, 'asc')())\
        .filter(Article.agency!=None)\
        .paginate(page, per_page, True)
    next = (url_for('articles', page=page+1, sort=sort, direction=direction) if
            arts.has_next else None)
    prev = (url_for('articles', page=page-1, sort=sort, direction=direction) if
            arts.has_prev else None)
    return render_template('articles.html', articles=arts.items, pages=pages,
                           sort=sort, page=page, direction=direction,
                           per_page=per_page, per_pages=per_pages,
                           next=next, prev=prev)

@app.route('/docs/<doc>')
def docs(doc):
    """Get a static document and serve it."""
    root = 'static/docs/'
    path = root + doc + '.md'
    try:
        f = app.open_resource(path, mode='rt').read()
    except:
        abort(404)
    return render_template('docs.html', doc=f)
