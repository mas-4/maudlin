from newscrawler import app
from newscrawler.models import Article

@app.route('/')
def index():
    count = Article.query.count()
    return str(count)
