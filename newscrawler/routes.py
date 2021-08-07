import math, io, string, time, os
import requests as rq
from datetime import date
from flask import (render_template, send_file, request, current_app, abort,
                   url_for)
from sqlalchemy import func, asc, desc
from newscrawler import app, db
from newscrawler.models import Agency, Article
from newscrawler.utils import pagination
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
    PER_PAGE = 3
    pages = list(range(1, math.ceil(Agency.query.count() / PER_PAGE)+1))
    t = timing(t, "getting sorts and pages")

    try:
        route = '/listjobs.json?project=newscrawler'
        url = current_app.config['SCRAPY_URL'] + route
        usr = current_app.config['SCRAPY_USR']
        pwd = current_app.config['SCRAPY_PWD']
        jobs = rq.get(url, auth=(usr,pwd)).json()
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
        overall=Article.todays_sentiment(), running=jobs['running'],
        active='index')
    timing(t, "rendering template")
    return html


@app.route('/agencies')
def agencies():
    """List of all agencies"""
    sort = request.args.get('sort', default='Name')
    page = request.args.get('page', default='1')
    per_page = 6
    try:
        page = int(page)
    except:
        abort(404)
    sorts = {
        'Name': Agency.query.order_by(Agency.name),
        'Sentiment': Agency.query.order_by(Agency.cum_sent.desc()),
        'Neutrality': Agency.query.order_by(Agency.cum_neut.desc()),
        'Articles': (Agency.query.join(Article).group_by(Agency.id)
                        .order_by(db.func.count(Article.id).desc())),
    }
    maxpages = math.ceil(Agency.query.count() / per_page)
    pages = pagination(page, maxpages)
    agencies = sorts[sort].paginate(page, per_page, False)
    return render_template('agencies.html', agencies=agencies.items,
                           sorts=sorts.keys(), sort=sort,
                           page=page, pages=pages, active='agencies')


@app.route('/agency/<agency>')
def agency(agency):
    """Data for a particular agency"""
    agency = Agency.query.filter(Agency.name == agency).first_or_404()
    return render_template('agency.html', agency=agency, Article=Article,
                           active='agency')


stopwords = list(STOPWORDS)
# clean some default words
stopwords.extend(['say', 'said', 'says', "n't", 'Mr', 'Ms', 'Mrs'])
# strip stray letters
stopwords.extend([l for l in string.ascii_lowercase + string.ascii_uppercase])
# Parts of Speech to keep
POS = [
    'FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'RB',
    'RBR', 'RBS', 'RP', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VNP', 'VBZ']

def rawwordcloud(text, scale, width=150, height=80, POS=POS):
    t = time.time()
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
        width=width, height=height, background_color='white',
        stopwords=stopwords, scale=scale)\
        .generate(text).to_array()
    t = timing(t, "generating wordcloud")

    # Make image
    img = Image.fromarray(wordcloud.astype('uint8'))
    timing(t, "generating image")
    return img


def wordcloud(text, scale, width=150, height=80, POS=POS):
    img = rawwordcloud(text, scale, width, height, POS)
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)

    return send_file(file_object, mimetype='image/png')


@app.route('/agency/<agency>/wordcloud')
def agencywordcloud(agency):
    """Generate a wordcloud for today's articles, or the last 15 articles"""
    scale = request.args.get('scale', default=5)
    try:
        scale = int(width)
        app.logger.info(scale)
    except:
        scale = 5
    agency = Agency.query.filter(Agency.name == agency).first_or_404()
    articles = agency.articles.order_by(Article.date.desc()).limit(15).all()

    text = []
    for article in articles:
        text.append(article.text)
    text = ' '.join(text)
    return wordcloud(text, scale)


@app.route('/wordcloud')
def daywordcloud():
    """Generate a wordcloud for today's articles, or the last 15 articles"""
    t = time.time()
    scale = request.args.get('scale', default=5)
    try:
        scale = int(width)
        app.logger.info(scale)
    except:
        scale = 5
    articles = Article.query.filter(Article.date==date.today()).all()
    t = timing(t, "getting articles")

    text = []
    for article in articles:
        text.append(article.text)
    text = ' '.join(text)
    t = timing(t, "joining text")
    return wordcloud(text, 1, width=1280, height=720, POS=['NNP', 'NNPS', 'NN', 'NN'])


DIRECTIONS = {'asc': asc, 'desc': desc}
def get_args(request):
    page = request.args.get('page', default='1')
    try:
        page = int(page)
    except:
        abort(404)
    sort = request.args.get('sort', default='date')
    direction = request.args.get('direction', default='asc')
    if direction in DIRECTIONS.keys():
        dirfunc = DIRECTIONS[direction]
    else:
        dirfunc = DIRECTIONS['asc']
    per_page = int(request.args.get('per_page', default='50'))
    print(direction)

    return page, sort, direction, dirfunc, per_page

@app.route('/articles')
def articles():
    """A table of all articles"""
    per_pages = [10, 25, 50, 100, 250, 500]
    page, sort, direction, dirfunc, per_page = get_args(request)
    q = Article.query
    sorts = {
        'agency': q.join(Article.agency).order_by(dirfunc(Agency.name)),
        'title': q.order_by(dirfunc(Article.title)),
        'date': q.order_by(dirfunc(Article.date)),
        'byline': q.order_by(dirfunc(Article.byline)),
        'pos': q.order_by(dirfunc(Article.pos)),
        'neg': q.order_by(dirfunc(Article.neg)),
        'neu': q.order_by(dirfunc(Article.neu)),
        'compound': q.order_by(dirfunc(Article.compound)),
        'sent': q.order_by(dirfunc(Article.sent))
    }
    maxpages = math.ceil(Article.query.count() / per_page)
    pages = pagination(page, maxpages)
    arts = sorts.get(sort, sorts['date'])\
        .filter(Article.agency!=None)\
        .paginate(page, per_page, True)
    next = (url_for('articles', page=page+1, sort=sort, direction=direction) if
            arts.has_next else None)
    prev = (url_for('articles', page=page-1, sort=sort, direction=direction) if
            arts.has_prev else None)
    return render_template('articles.html', articles=arts.items, pages=pages,
                           sort=sort, page=page, direction=direction,
                           per_page=per_page, per_pages=per_pages,
                           next=next, prev=prev, active='articles')


@app.route('/docs/<doc>')
def docs(doc):
    """Get a static document and serve it."""
    root = 'static/docs/'
    path = root + doc + '.md'
    try:
        f = app.open_resource(path, mode='rt').read()
    except:
        abort(404)
    return render_template('docs.html', doc=f, active='doc')
