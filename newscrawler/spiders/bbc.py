import re

from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article


class BbcSpider(scrapy.Spider, BoilerPlateParser):
    name = 'bbc'
    allowed_domains = ['bbc.com', 'bbc.co.uk']
    start_urls = ['https://www.bbc.com']

    def parse(self, response):
        soup = BS(response.text, 'lxml')
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = response.css('#main-heading::text').get()
            item['byline'] = None # No byline on the bbc

            date = soup.find('time')
            date = parser.parse(date['datetime'])
            item['date'] = date

            paragraphs = soup.find_all('div', attrs={'data-component': 'text-block'})
            item['text'] = self.joinparagraphs(paragraphs)
            if not item['text']:
                yield None
            else:
                yield item

        if response.url == self.start_urls[0]:
            attrs={'href': re.compile('/news/.*-\d+$')}
            links = set(a['href'] for a in soup.find_all('a', attrs=attrs))
            for link in links:
                if Article.query.filter(Article.url.endswith(link)).first():
                    continue
                yield response.follow(link, callback=self.parse)
