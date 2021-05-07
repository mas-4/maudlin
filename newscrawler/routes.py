from flask import render_template
from newscrawler import app
from newscrawler.models import Article

@app.route('/')
def index():
    count = Article.query.count()
    return render_template('index.html', count=count)
