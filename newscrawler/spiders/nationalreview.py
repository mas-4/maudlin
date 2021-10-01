import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class NationalReviewSpider(scrapy.Spider, BoilerPlateParser):
    name = 'nationalreview'
    allowed_domains = ['www.nationalreview.com']
    start_urls = ['https://www.nationalreview.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': re.compile('article-header__title')}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            byline = None

            tag = 'time'
            attrs = {'class': re.compile('pubdate')}
            date = soup.find(tag, attrs)
            date = date['datetime']
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': re.compile('article-content')}
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
