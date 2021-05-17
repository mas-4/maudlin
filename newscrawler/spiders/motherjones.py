import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class MotherjonesSpider(scrapy.Spider, BoilerPlateParser):
    name = 'motherjones'
    allowed_domains = ['www.motherjones.com']
    start_urls = ['https://www.motherjones.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': 'entry-title'}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'a'
            attrs = {'rel': 'author'}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'meta'
            attrs = {'name': 'sailthru.date'}
            date = soup.find(tag, attrs)
            date = parser.parse(date['content'])

            tag = 'article'
            attrs = {'class': 'entry-content'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'/\d{4}/\d{2}/(?!toc)')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
