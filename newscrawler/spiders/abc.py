import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class AbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'abc'
    allowed_domains = ['abcnews.go.com']
    start_urls = ['https://abcnews.go.com/']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            tag = 'h1'
            attrs = {'class': re.compile('Article__Headline__Title')}
            title = soup.find(tag, attrs=attrs).text.strip()

            byline = None

            tag = 'div'
            attrs = {'class': re.compile('Byline__Meta Byline__Meta--publishDate')}
            date = soup.find(tag, attrs=attrs)
            date = parser.parse(date.text.strip())

            tag = 'section'
            attrs = {'class': re.compile('Article__Content story')}
            root = soup.find(tag, attrs=attrs)
            paragraphs = root.find_all('p')
            text = self.joinparagraphs(paragraphs)


            item = self.populate_item(title, byline, date, text, item)
            yield item

        if response.url == self.start_urls[0]:
            attrs = {'class': 'AnchorLink', 'href': re.compile(r'http.*\d?id=\d+$')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
