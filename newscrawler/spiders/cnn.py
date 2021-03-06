from bs4 import BeautifulSoup as BS
from dateutil import parser
import scrapy

from newscrawler.mixins import BoilerPlateParser
from newscrawler.models import Article

CLASS = 'afe4286c'

class CnnSpider(scrapy.Spider, BoilerPlateParser):
    name = 'cnn'
    allowed_domains = ['cnn.com']
    start_urls = ['http://lite.cnn.com/en']


    def parse(self, response):
        if response.url != self.start_urls[0]:
            item = self.prepopulate_item(response)

            item['title'] = response.css('h2::text').get()
            item['byline'] = response.css('#byline::text').get()

            date = response.css('#published\ datetime::text').get()
            date = ''.join(date.split(':')[1:]).strip()
            date = parser.parse(date)
            item['date'] = date

            soup = BS(response.text, 'lxml')
            article = soup.find('div', class_=CLASS)
            paragraphs = article.find_all('p', id=None)
            item['text'] = self.joinparagraphs(paragraphs)
            yield item

        for article in response.css('li > a::attr(href)'):
            link = article.get()
            if Article.query.filter(Article.url.endswith(link)).first():
                continue
            yield response.follow(link, callback=self.parse)
