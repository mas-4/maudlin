import argparse
from datetime import date, datetime

from newscrawler import db
from newscrawler.models import Article
from newscrawler.routes import rawwordcloud

def main(path):
    """Generate a wordcloud for today's articles, or the last 15 articles"""
    print(db)
    articles = Article.query.filter(Article.date==date.today()).all()

    text = []
    for article in articles:
        text.append(article.text)
    text = ' '.join(text)
    img = rawwordcloud(text, 1, width=1280, height=720, POS=['NNP', 'NNPS', 'NN', 'NN'])
    with open(path + '/' +  datetime.now().strftime('%Y%m%d-%H%M') + '.png', 'wb') as fout:
        img.save(fout, 'PNG')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, action='store')
    args = parser.parse_args()
    main(args.path)
