import os
from datetime import date
from newscrawler import celery_app
from .models import Article
from .routes import wordcloud


@celery_app.task()
def make_wordcloud_today():
    """Generate a wordcloud for today's articles"""
    articles = Article.query.filter(Article.date==date.today()).all()

    text = []
    for article in articles:
        text.append(article.text)
    text = ' '.join(text)
    wc = wordcloud(text, 1, width=1000, height=500, POS=['NNP', 'NNPS', 'NN',
                                                           'NN'])
    with open('newscrawler/static/images/today.png', 'wb') as fout:
        fout.write(wc.read())

CELERYBEAT_SCHEDULE = {
    'make_wordcloud_today': {
        'task': 'newscrawler.tasks.make_wordcloud_today',
        'schedule': 10 * 60
    },
}

celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE
