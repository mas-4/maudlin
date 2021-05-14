import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class BusinessinsiderSpider(scrapy.Spider, BoilerPlateParser):
    name = 'businessinsider'
    allowed_domains = ['businessinsider.com']
    start_urls = ['https://www.businessinsider.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': 'post-headline'}
            title = soup.find(tag, attrs=attrs)
            tag = 'h1'
            attrs = {'class': 'article-title'}
            if not title:
                title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'div'
            attrs = {'class': 'byline-author'}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'div'
            attrs = {'class': 'byline-timestamp'}
            date = soup.find(tag, attrs)
            date = date['data-timestamp']
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': 'content-lock-content'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'[-0-9]{7,8}')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
