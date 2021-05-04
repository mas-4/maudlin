import scrapy
from dateutil import parser
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup as BS
from newscrawler.mixins import BoilerPlateParser
import logging

CLASS = 'article-body'

class FoxCrawler(CrawlSpider, BoilerPlateParser):
    name = 'fox'
    allowed_domains = ['www.foxnews.com']
    start_urls = ['https://www.foxnews.com/']
    rules = [
        Rule(LinkExtractor(allow='.*'), follow=True, callback='parse')
    ]


    def parse(self, response):
        item = self.prepopulate_item(response)

        item['title'] = response.css('h1.headline::text').get()
        # fragile
        item['byline'] = response.css('.author-byline > span:nth-child(2) > span:nth-child(1) > a:nth-child(1)::text').get()

        if not item['byline']:
            return None

        soup = BS(response.text, 'lxml')

        date = soup.find('meta', attrs={'name': 'dc.date'})
        if not date['content']:
            return None
        date = parser.parse(date['content'])
        item['date'] = date

        text = soup.find('div', class_=CLASS)
        if not text:
            return None

        paragraphs = text.find_all('p')
        text = self.joinparagraphs(paragraphs)

        # replace nbsp
        item['text'] = text.replace('\xa0', ' ')

        return item
