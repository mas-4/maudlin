import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class NypostSpider(scrapy.Spider, BoilerPlateParser):
    name = 'nypost'
    allowed_domains = ['nypost.com']
    start_urls = ['https://nypost.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': re.compile('headline')}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'p'
            attrs = {'class': 'byline'}
            byline = None

            tag = 'meta'
            attrs = {'property': 'article:published_time'}
            date = soup.find(tag, attrs)
            date = date['content']
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': 'entry-content'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{2}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
