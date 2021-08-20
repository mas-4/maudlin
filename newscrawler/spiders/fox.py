import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article

CLASS = 'article-body'

class FoxSpider(scrapy.Spider, BoilerPlateParser):
    name = 'fox'
    allowed_domains = ['feeds.foxnews.com', 'www.foxnews.com']
    start_urls = ['https://www.foxnews.com']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = response.css('h1.headline::text').get()
            # fragile
            item['byline'] = response.css('.author-byline > span:nth-child(2) > span:nth-child(1) > a:nth-child(1)::text').get()

            date = soup.find('meta', attrs={'name': 'dc.date'})
            if date['content']:
                date = parser.parse(date['content'])
                item['date'] = date

            text = soup.find('div', class_=CLASS)
            if not text:
                return None

            paragraphs = text.find_all('p')
            # filter out ad paragraphs, which are always all caps
            paragraphs = list(filter(lambda l: l.text.strip().upper() != l.text.strip(), paragraphs))
            text = self.joinparagraphs(paragraphs)
            item['text'] = text

            yield item

        if response.url == self.start_urls[0]:
            root = soup.find('div', class_='page-content')
            attrs={'href': re.compile(r'https://www.foxnews.com/.+/[-a-z0-9]+$')}
            links = set(a['href'] for a in root.find_all('a', attrs=attrs))
            for link in links:
                if '/cartoons-slideshow' not in link:
                    if Article.query.filter(Article.url.endswith(link)).first():
                        continue
                    yield response.follow(link, callback=self.parse)
