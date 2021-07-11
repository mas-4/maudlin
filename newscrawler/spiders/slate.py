from newscrawler.models import Article
import scrapy
from datetime import date as dt
from dateutil import parser
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser


class SlateSpider(scrapy.Spider, BoilerPlateParser):
    name = 'slate'
    allowed_domains = ['slate.com']
    start_urls = ['https://slate.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = soup.find(
                'h1', attrs={'class': 'article__hed', 'itemprop': 'headline'})\
                .text.strip()
            byline = soup.find('div', class_='article__byline')
            try:
                byline = byline.find('a').text.strip()
            except:
                byline = byline.text.strip()
            item['byline'] = byline


            date = soup.find('time', class_='article__dateline')['content']
            date = parser.parse(date)
            item['date'] = date

            article = soup.find('div', class_='article__content')
            paragraphs = article.find_all('p')
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('main', id='main')
            for a in root.find_all('a'):
                try:
                    if str(dt.today().year) in a['href']:
                        if Article.query.filter(Article.url.endswith(a['href'])).first():
                            continue
                        if '/podcasts/' in a['href']:
                            continue
                        yield response.follow(a['href'], callback=self.parse)
                except:
                    continue
