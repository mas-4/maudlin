from newscrawler import app, db
from newscrawler.models import Article, Agency

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Article': Article, 'Agency': Agency}
