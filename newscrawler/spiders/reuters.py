import re
import scrapy
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
from dateutil import parser


class ReutersSpider(scrapy.Spider, BoilerPlateParser):
    name = 'reuters'
    allowed_domains = ['www.reuters.com']
    start_urls = ['https://www.reuters.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')

        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': re.compile(r'ArticleHeader')}
            title = soup.find(tag, attrs=attrs)
            title = title.text.strip()

            tag = 'div'
            attrs = {'class': re.compile('ArticleHeader__author')}
            byline = soup.find(tag, attrs=attrs)
            byline = re.sub('  +', ' ', byline.text.strip()) if byline else None

            tag = 'time'
            attrs = {'class': re.compile('ArticleHeader__dateline')}
            date = soup.find(tag, attrs)
            date = date.span.text.strip()
            date = parser.parse(date)

            tag = 'div'
            attrs = {'class': re.compile('ArticleBody__container')}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'href': re.compile(r'-\d{4}-\d{2}-\d{2}')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                yield response.follow(link, callback=self.parse)
