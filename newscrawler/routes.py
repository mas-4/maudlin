from flask import render_template
from newscrawler import app
from newscrawler.models import Agency, Article
from datetime import date

def color(num):
    h = (num*155) / 100
    h += 100
    h = abs(h)
    d = str(hex(int(h))) # convert to hex and strip x
    d = format(int(h), 'x')
    d = d.zfill(2)
    if num > 0:
        color = f'00{d}00'
    else:
        color = f'{d}0000'
    return color

@app.route('/')
def index():
    articles = Article.query.filter(Article.date==date.today()).all()
    structure = {}
    for article in articles:
        article.sentiment = round((article.pos - article.neg) * 100, 2)
        article.neutral = round(article.neu * 100, 2)
        article.color = color(article.sentiment)
        if article.agency in structure:
            structure[article.agency].append(article)
        else:
            structure[article.agency] = [article]
    return render_template('index.html',
                           count=len(articles),
                           structure=structure)
