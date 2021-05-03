# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from newscrawler.models import db_connect, create_table, Article
from sqlalchemy.orm import sessionmaker


class NewscrawlerPipeline:
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        article = Article()
        article.title = item['title']
        article.url = item['url']
        article.byline = item['byline']
        article.date = item['date']
        article.text = item['text']

        exists = session.query(Article).filter_by(title=article.title).first()
        if exists:
            return item
        try:
            session.add(article)
            session.commit()
        except Exception as e:
            print(article, e)
        finally:
            session.close()

        return item
