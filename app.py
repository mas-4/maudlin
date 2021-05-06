from flask import Flask
from newscrawler.models import Article, Agency, get_session

app = Flask(__name__)

@app.route('/')
def index():
    with get_session() as s:
        count = s.query(Article).count()
    return str(count)
