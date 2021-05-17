import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class ApSpider(scrapy.Spider, BoilerPlateParser):
    name = 'ap'
    allowed_domains = ['apnews.com']
    start_urls = ['https://apnews.com/']


    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'div'
            attrs = {'data-key': 'card-headline'}
            title = soup.find(tag, attrs=attrs).h1
            title = title.text.strip()

            tag = 'span'
            attrs = {'class': re.compile('Component-bylines')}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'span'
            attrs = {'data-key': 'timestamp'}
            date = soup.find(tag, attrs)
            date = date['data-source'].strip()
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': 'Article'}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'^/article/')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
