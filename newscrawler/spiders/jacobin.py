import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class JacobinSpider(scrapy.Spider, BoilerPlateParser):
    name = 'jacobin'
    allowed_domains = ['jacobinmag.com']
    start_urls = ['https://jacobinmag.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': 'po-hr-cn__title'}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'dd'
            attrs = {'class': 'po-hr-cn__author'}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'time'
            attrs = {'class': 'po-hr-fl__date'}
            date = soup.find(tag, attrs)
            date = date.text.strip()
            date = parser.parse(date)

            tag = 'div'
            attrs = {'id': 'post-content'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{2}/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
